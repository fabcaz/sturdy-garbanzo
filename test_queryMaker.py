import unittest
from datetime import datetime, timedelta
import queryMaker
import logging
import sys

logFileName = datetime.strftime(datetime.now() , "%d-%m-%Y_%H-%M")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler_stdout = logging.StreamHandler(sys.stdout)
handler_to_file = logging.FileHandler( logFileName+ "_test_querryMaker.log", encoding="utf-8")
handler_stdout.setFormatter(
    logging.Formatter('%(asctime)s::%(levelname)s::%(module)s:%(message)s')
)
handler_to_file.setFormatter(
    logging.Formatter('%(asctime)s::%(levelname)s::%(module)s:%(message)s')
)
logger.addHandler(handler_stdout)
logger.addHandler(handler_to_file)

logger.debug(sys.argv[0])

class TestQueryMaker(unittest.TestCase):
    #JAN_01_2022.weekday() >>> 5
    #Saturday January 1, 2022
    JAN_01_2022 = datetime(2022, 1, 1)

    #JUN_30_2022.weekday() >>> 3
    #Thursday June 30 ,2022
    JUN_30_2022 = datetime(2022, 6, 30)
    
    
    #@unittest.skip("to reduce noise")
    def test_adjustRangeBounds_early_start(self):
    """should adjust start to later in the same week
    """
        logger.debug("\n===" + self.id())
        initStartOffset = timedelta(days=2)
        start = self.JAN_01_2022 + initStartOffset # monday Jan 3, 2022
        end   = self.JUN_30_2022
        weekday = 6 #sunday
        # end date should be: sun jan 9 2022

        logger.debug("initial start date: " + str(start))
        start, end = queryMaker.adjustRangeBounds(start, end, weekday)
        
        logger.debug("resulting start date: " + str(start))
        self.assertEqual(start.weekday(), weekday)
        self.assertEqual(start - (self.JAN_01_2022+initStartOffset), timedelta(days=6))
        self.assertEqual(start, datetime(2022, 1, 9))

    #@unittest.skip("to reduce noise")
    def test_adjustRangeBounds_late_start(self):
    """should adjust start to following week
    """
        logger.debug("\n===" + self.id())

        start = self.JAN_01_2022
        end   = self.JUN_30_2022
        weekday = 1 # tuesday
        # end date should be: tue jan 4 2022

        logger.debug("initial start date: " + str(start))
        start, end = queryMaker.adjustRangeBounds(start, end, weekday)

        logger.debug("resulting start date: " + str(start))
        self.assertEqual(start.weekday(), weekday)
        self.assertEqual(start - self.JAN_01_2022, timedelta(days=3))
        self.assertEqual(start, datetime(2022, 1, 4))


    #@unittest.skip("to reduce noise")
    def test_adjustRangeBounds_early_end(self):
    """ should move end date to previous occurrence of weekday
    """
        logger.debug("\n===" + self.id())


        start = self.JAN_01_2022
        end   = self.JUN_30_2022
        weekday = 5 # saturday
        # end date should be: sat june 25 2022

        logger.debug("initial end date: " + str(end))
        start, end = queryMaker.adjustRangeBounds(start, end, weekday)

        logger.debug("resulting end date: " + str(end))
        self.assertEqual(end.weekday(), weekday)
        self.assertEqual(end - self.JUN_30_2022, timedelta(days=-5))
        self.assertEqual(end, datetime(2022, 6, 25))

    #@unittest.skip("to reduce noise")
    def test_adjustRangeBounds_late_end(self):
    """ should move end date to previous occurrence of weekday
    """
        logger.debug("\n===" + self.id())


        start = self.JAN_01_2022
        end   = self.JUN_30_2022
        weekday = 1 # tuesday
        # end date should be: tue june 28 2022

        logger.debug("initial end date: " + str(end))
        start, end = queryMaker.adjustRangeBounds(start, end, weekday)

        logger.debug("resulting end date: " + str(end))
        self.assertEqual(end.weekday(), weekday)
        self.assertEqual(end - self.JUN_30_2022, timedelta(days=-2))
        self.assertEqual(end, datetime(2022, 6, 28))

    # only checking for 7day intervals since that's the only use case

    #@unittest.skip("to reduce noise")
    def test_generateFormatedDates(self):
        ''' checks for week lengthed cycles
        '''
        start = datetime(2021, 6, 6)
        end   = datetime(2021, 12, 26)
        desiredWeekDay = 6

        result = queryMaker.generateFormatedDates(start, end)
        self.assertEqual(len(result), 29)

        #if a date's weekday isn't correct, the fn would throw, but check anyways
        for date in result:
            currDate = datetime.strptime(date, "%d-%m-%Y")
            logger.debug(str(currDate).split(' ')[0]+" has day= "+str(currDate.weekday()))

            self.assertEqual(currDate.weekday(), desiredWeekDay)




if __name__ == "__main__":
    unittest.main()
