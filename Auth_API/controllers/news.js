const axios = require('axios');
const cheerio = require('cheerio');

const baseurl = 'https://www.suara.com/tag/daur-ulang-sampah';
const baseurlPrefix = 'https://www.suara.com';

async function getNews(req, res) {
    try {
        const response = await axios.get(baseurl);
        const $ = cheerio.load(response.data);

        const news_data = [];

        // Selektor disesuaikan dengan struktur HTML yang diberikan
        const news = $(".item");
        news.each(function () {
            let thumbnail = $(this).find(".img-thumb-4 img").attr("src");
            if (thumbnail && !thumbnail.startsWith('http')) {
                thumbnail = baseurlPrefix + thumbnail; // Menambahkan URL awalan jika thumbnail bukan URL absolut
            }
            const title = $(this).find(".text-list-item-y a").text().trim();
            let link = $(this).find(".text-list-item-y a").attr("href");
            if (link && !link.startsWith('http')) {
                link = baseurlPrefix + link; // Menambahkan URL awalan jika link bukan URL absolut
            }

            

            news_data.push({ thumbnail, title, link });
        });

        res.json(news_data);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Failed to fetch news' });
    }
}

module.exports = {
    getNews
};
