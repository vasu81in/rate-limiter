
import time
import collections

class RateLimiter:
    def __init__(self, interval=60, max_events=100):
        self.cache = {}
        self.interval = interval
        self.max_events = max_events
        self.cur_window = int(time.time()) # epoch since 1,1,1970 in seconds

    def should_allow(self, key):
        print(f'received req: {key}')
        current_time = int(time.time())
        
        # if the current time exceeds the current window, 
        # delete the current window and reset the hashmap to the new window
        # that starts from the current time
        if current_time - self.cur_window > self.interval:
            print(f'delete the old start window {self.cur_window}')
            del self.cache[self.cur_window]
            print(f'mark the start of new window {self.cur_window}') 
            self.cur_window = int(current_time)

        # use the current window to rate limit the requests
        if self.cur_window not in self.cache:
            self.cache[self.cur_window] = collections.defaultdict(int)
            self.cache[self.cur_window][key] = 1
            return True

        # if the key is found and the count is > max_events,
        # drop the req. Otherwise, allow and increment the counter. 
        print(f'allow req {key} in cur window {self.cur_window}')
        window = self.cache[self.cur_window]
        if window[key]  >= self.max_events:
            print(f'drop req {key} due to rate limiting exceeding threshold')
            return False
        
        window[key] += 1
        return True

from ratelimiter import RateLimiter
import unittest
import random

class TestRateLimiter(unittest.TestCase):
    def setup(self):
        print("\nRunning setUp method...")
        self.rl = RateLimiter()

    def tearDown(self):
        print("\nRunning tearDown method...")
        self.rl = None
    
    def test_should_allow(self):
        print("\nRunning tests ...")
        rt = RateLimiter()
        startTime =  int(time.time())

        requests = ["1.2.3.4", '1.3.4.6', '1.2.4.3']
        interval = 60
        
        stats = {}
        while int(time.time()) - startTime < interval:
            time.sleep(0.1)
            req = random.choice(requests)
            if req not in stats:
                stats[req] = [0, 0, int(time.time())] # allow, drop, curr_time
            
            if not rt.should_allow(req):
                stats[req][1] += 1
                stats[req][2] = int(time.time())
            else:
                stats[req][0] += 1
                stats[req][2] = int(time.time())

        for s,v in stats.items():
            self.assertEqual(stats[s][0], 100)
            self.assertGreaterEqual(stats[s][1], 0)

        print("\n\n----------------- rate limiter test stats --------------------\n")
        print(f'\n\nrate limiter cache: {rt.cache}\n\n')
        for s,v in stats.items():
            print(f'req: {req} allow: {v[0]} drop: {v[1]} epoch: {v[2]}')

if __name__ == '__main__':
    unittest.main()
