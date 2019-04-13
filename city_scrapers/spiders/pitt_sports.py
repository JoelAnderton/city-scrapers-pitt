from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import re
from datetime import datetime

class PittSportsSpider(CityScrapersSpider):
    name = "pitt_sports"
    agency = "Sports and Exhibition Authority"
    timezone = "US/Eastern"
    allowed_domains = ["pgh-sea.com"]
    start_urls = ["http://www.pgh-sea.com/schedule_sea.aspx?yr=2018"]


    def parse(self, response):
        year_links = response.xpath('//div[@class="projectlink"]/a/@href').extract()

        for year_link in year_links:
            year_link = 'http://www.pgh-sea.com/' + year_link
            year = CityScrapersSpider.Request(url=year_link, callback=self.parse2)
            yield year

    def parse2(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # item = MeetingItem()
        meetings = response.xpath('//tr[@class="ScheduleTextBold"]/td/text()').extract()[3:]
        #print(item)

        for item in meetings:
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "SEA Board Meeting"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        for date in item:
            # Style 1 - No time (not all the dates have times)
            try:
                day_year = date.split(', ')
                day_year = day_year[1:]  # get the days and years
                day = day_year[0]  # select the days
                year = day_year[1]  # select the years
                time = '10:30AM'  # using 10:30am as default time since that's what the website says
                new_date = day + ' ' + year + ' ' + time  # concatenate the days and years

                date = datetime.datetime.strptime(new_date, '%b %d %Y %I:%M%p')  # convert to a date
                item['date'] = date
                return (item['date'])

            except:
                # Style 2 - With time
                try:
                    date = date.split(', ')
                    day = date[1]  # get the days
                    year = date[2][:4]  # get the years
                    time = date[2][8:].replace(' ', '')  # get the times

                    date = day + ' ' + year + ' ' + time  # concatenate the days, years, and times together

                    date = datetime.datetime.strptime(date, '%b %d %Y %I:%M%p')  # convert to a date

                    item = date
                    return (item)
                except Exception as e:
                    pass

        return item

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "1000 Fort Duquesne Blvd, Pittsburgh, PA 15222",
            "name": "David L. Lawrence Convention Center Room 333",
        }

    def _parse_links(self, response):
        """Parse or generate links."""

        link = response.xpath('//a[@class="ScheduleTextBold"]/@href').extract()[3:]
        link_text = response.xpath('//a[@class="ScheduleTextBold"]/text()').extract()[3:]
        links_zipped = zip(link, link_text)

        for item in links_zipped:
            links = [{"href": item[0], "title": item[1]}]
            return (links)



    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
