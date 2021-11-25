const fs = require("fs");
const axios = require("axios")
const wtf = require("wtf_wikipedia")
const ObjectsToCSV = require("objects-to-csv")
const {Translate} = require('@google-cloud/translate').v2
const config = require('./config')

wtf.extend(require('wtf-plugin-summary'))
wtf.extend(require('wtf-plugin-person'))

const translate = new Translate({
    projectId: config.projectId,
    keyFilename: config.keyFilename
})

singersListUrl = "https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:21st-century_English_women_singers&cmlimit=500&format=json"

scrapeData() 

async function scrapeData() {
    try {
        const singers = []
        const singersTranslated = []
        const pages = await getTitles(singersListUrl)
        console.log(pages.length)
        for (let i=0; i < pages.length; i++) {
            const singerData = await getContent(pages[i].title)
            if (Object.values(singerData).filter(value => value !== 'N/A' || value !== '').length >= 7) {
                const translatedData = await translateContent(singerData)
                singers.push(singerData)
                singersTranslated.push(translatedData)
            console.log(translatedData.name_en)
            }
        }
        console.log(singers.length)
        const originalDataCsv = new ObjectsToCSV(singers)
        originalDataCsv.toDisk("./data_original.csv")
        fs.writeFileSync("./data_processed.json", JSON.stringify(singersTranslated, null, 4));
    }
    catch(err){
        console.log(err)
    }
}


async function getTitles(url) {
    try {
        const response = await axios.get(url)
        const data = response.data
        const pages = data.query.categorymembers
        return pages
    }
    catch(err) {
        throw err
    }
}

async function getContent(title) {

    try {
        const doc = await wtf.fetch(title)
        let personalInfo = doc.section('Early life') || doc.section('Biography') || doc.section('Personal life')
        let careerInfo = doc.section('Career') || doc.section('Music career')
        let awards = doc.section('Awards') || doc.section('Awards and nominations')
        let discography = doc.section("discography") 
        const summary = doc.summary()
        const link = doc.url()

        let yearsActive = 'N/A'
        if (doc.infoboxes()[0] && doc.infoboxes()[0].get("years_active") && doc.infoboxes()[0].get("years_active").json().text!==""){
            yearsActive = doc.infoboxes()[0].get("years_active").json().text
        }
        
        let genre = 'N/A'
        if (doc.infoboxes()[0] && doc.infoboxes()[0].get("genre") && doc.infoboxes()[0].get("genre").json().text !== ""){
            genre = doc.infoboxes()[0].get("genre").json().text
        }

        let birthDate = 'N/A'
        if (doc.birthDate()) {
            birthDate = doc.birthDate().year
            if (doc.birthDate().date && doc.birthDate().month) {
                birthDate = doc.birthDate().date + '/' + doc.birthDate().month + '/' + birthDate
            }
        }    

        personalInfo = readSection(personalInfo)
        careerInfo = readSection(careerInfo)
        awards = readSection(awards)
        discography = readSection(discography)

        const singerData = {
            name: title,
            personalInfo: personalInfo,
            careerInfo: careerInfo,
            discography: discography,
            awards: awards,
            summary: summary,
            birthDate: birthDate,
            yearsActive: yearsActive,
            genre: genre,
            link: link
        }

        return singerData
    }
    catch(err) {
        console.log(err)
    }
}

function readSection(field) {
    let data = ''
    if (!field) {
        data = "N/A"
    } else if (field.children().length > 0) {
        for (let i=0; i < field.children().length; i++) {
            data += readSection(field.children()[i])
        }
    } else {
        data = field.text()

        if (field.tables().length > 0) {
            const tables = field.tables()
            for (let i=0; i < tables.length; i++) {
                for (let j=0; j < tables[i].keyValue().length; j++) {
                    data += Object.values(tables[i].keyValue()[j]).filter(value => value !== '' && value !== '—').join('—') + ','
                }
            }
        }
    }
    return data
}

async function translateContent(singer) {
    const [name_si] = await translate.translate(singer.name, 'si')
    const [personalInfo_si] = await translate.translate(singer.personalInfo, 'si')
    const [careerInfo_si] = await translate.translate(singer.careerInfo, 'si')
    const [discography_si] = await translate.translate(singer.discography, 'si')
    const [award_si] = await translate.translate(singer.awards, 'si')
    const [summary_si] = await translate.translate(singer.summary, 'si')
    const [yearsActive_si] = await translate.translate(singer.yearsActive, 'si')
    const [genre_si] = await translate.translate(singer.genre, 'si')

    const singersTranslated = {
        name_en: singer.name,
        name_si: name_si,
        personalInfo_en: singer.personalInfo,
        personalInfo_si: personalInfo_si,
        careerInfo_en: singer.careerInfo,
        careerInfo_si: careerInfo_si,
        discography_en: singer.discography,
        discography_si: discography_si,
        awards_en: singer.awards,
        award_si: award_si,
        summary_en: singer.summary,
        summary_si: summary_si,
        birthDate: singer.birthDate,
        yearsActive_en: singer.yearsActive,
        yearsActive_si: yearsActive_si,
        genre_en: singer.genre,
        genre_si: genre_si,
        link: singer.link
    }
    return singersTranslated
}