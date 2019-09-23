# Script was written MacOS Mojave 10.14.6 and Python 3.7.0 64-bit
import requests, os, random, time, subprocess, hashcommands, pprint

test_results = []

# Requirement 1: When launched, application should wait for http connection
# Test 1: Try FTP? - not tested
# Test 2: Try other Transfer Protocals? - not tested

# Requirement 2: It should answer on the PORT specified in the PORT environment variable.
### Not finding a quick answer on how to test that a response comes back over the same port that a call is made on,
### Would seek extra guidance or do more research on this if time permitted

def req_2_tests():
    req = 2
    test = 'Test 1: Make sure start & stop on 8088 works'
    try:
        port = hashcommands.start(8088)
        hashcommands.stop(port)
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 'notes':''})
    except Exception as exc:
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 'notes':'Exception for starting & stopping over port 8088 with exception: ' + exc})

    test = 'Test 2: Try another random port'
    try:
        port = hashcommands.start('random')
        hashcommands.stop(port)
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 'notes':''})
    except Exception as exc:
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 'notes':'Exception for starting & stopping over port' + port + 'with exception: ' + exc})

    # Test 3: Test no port
    ### Commented out because calls are defaulting over port 80
    # try:
    #     port = hashcommands.start(None)
    #     hashcommands.stop(port)
    # except Exception as exc:
    #     test_results.append('Exception for starting & stopping over port 8088 with exception: ' + exc)



# Requirement 3: A POST to /hash should accept a password. It should return a job identifier
# immediately. It should then wait 5 seconds and compute the password hash.
# The hashing algorithm should be SHA512.

# curl -X POST -H "application/json" -d '{"password":"angrymonkey"}' http://127.0.0.1:8088/hash

def req_3_tests():
    req = 2

    ### Requirement 3 Test 1
    test = 'Test 1: Test to make sure identifier is returned in under 1 second'
    
    port = hashcommands.start('random')
    response = requests.post('http://127.0.0.1:' + port + '/hash', '{"password":"angrymonkey"}')
    response_time = (response.elapsed.seconds)
    if response_time < 1:
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 
        'notes':''})
    else:
        test_results.append({'requirement': req, 'test':test, 'result':'fail', 
        'notes':'reponse took '+ str(response_time) + ' seconds'})

    ### Requirement 3 Test 2
    test = 'Test 2: Make sure base64 isn\'t returned before 5 seconds'

    # Start fresh instance of the hashing program to start at hash 1
    hashcommands.stop(port)
    port = hashcommands.start('random')
    # Create password request, force python to move to next steps instead of for a response because of the 5 second response bug
    try:
        requests.post('http://127.0.0.1:' + port + '/hash', '{"password":"angrymonkey"}', timeout=0.001)
    except requests.exceptions.ReadTimeout:        
        pass

    # Try every quarter second to see if the hash will return
    start_time = time.time()
    pass_fail = 'pass'
    for i in range(30):
        response = requests.get('http://127.0.0.1:' + port + '/hash/asdf')
        time_passed = time.time() - start_time
        print(response.text + ' at ' + str(time_passed) + ' seconds')
        if time_passed < 5 and str(response.text) != 'Hash not found\n':
            pass_fail = 'fail'
        time.sleep(0.25)
    if pass_fail == 'fail':
        test_results.append({'requirement': req, 'test':test, 'result':'fail', 
        'notes':'Hash not found should have been returned for all requests before 5 seconds and it wasn\'t'})
    else:
        test_results.append({'requirement': req, 'test':test, 'result':'pass', 'notes':''})

'''
Test 3: Check SHA512 to base64 is calculated properly using an outside source like https://approsto.com/sha-generator/

BUG: Job identifier takes 5 seconds to return
ISSUE: Hash changes if JSON key changes which would break logins if the key input changes
BUG: If an invalid request is made, it adds +1 to the Request count and brings down the average response time. 
     Perhaps those should be counted & response times for invalid requests calculated separately

3. If the JSON key of "password" changes, the hash changes, meaning the hash must be getting calculated from the JSON key plus the password. I would suggest only calculating the hash from the password value in case in the off chance a future dev changed the JSON key to "pass" rather than "password".

'''


'''
Requirement 4: A GET to /hash should accept a job identifier. It should return the base64
encoded password hash for the corresponding POST request.

curl -H "application/json" http://127.0.0.1:8088/hash/1 >
zHkbvZDdwYYiDnwtDdv/FIWvcy1sKCb7qi7Nu8Q8Cd/MqjQeyCI0pWKDGp74A1g==
'''

# def req_4_tests():
#     port = start_hash_program('random')
#     pw_submitted = 'before a password was submitted'
#     try:
#         response = requests.get('http://127.0.0.1:' + port + '/hash/0')
#         print(response.text, ' is the text reponse for trying hash identifier 0 ', pw_submitted)
#     try:
#         response = requests.get('http://127.0.0.1:' + port + '/hash/-1')
#         print(response.text, ' is the text reponse for trying hash identifier -1 ', pw_submitted)

#     submit_password('angrymonkey')
    
#     pw_submitted = 'after a password was submitted'
#     try:
#         response = requests.get('http://127.0.0.1:' + port + '/hash/0')
#         print(response.text, ' is the text reponse for trying hash identifier 0 ', pw_submitted)
#     try:
#         response = requests.get('http://127.0.0.1:' + port + '/hash/-1')
#         print(response.text, ' is the text reponse for trying hash identifier -1 ', pw_submitted)

'''
Test 1: Try -1 and 0 as identifiers
Test 2: Try integer bigger than how many identifiers there are
Test 3: Try letters and special characters
Test 4: Verify valid requests always return base64 (A-Z, a-z, 0-9, +, /, =)
Test 5: Enter same password twice, verify same base64 hash is returned
'''


'''
Requirement 5: A GET to /stats should accept no data. It should return a JSON data structure
for the total hash requests since the server started and the average time of a hash
request in milliseconds.

curl http://127.0.0.1:8088/stats >
{"TotalRequests":3,"AverageTime":5004625}

Test 1: Try sending data over a GET?
Test 2: Verify a valid return is JSON format with TotalRequests and AverageTime values
Test 3: Verify value of AverageTime
Test 4: Make sure response comes in under 50 milliseconds
'''


'''
Requirement 6: The software should be able to process multiple connections simultaneously.

Test 1: Test multiple simultaneous connections. 5, 20, 100, 1000 if possible
'''


'''
Requirement 7: The software should support a graceful shutdown request. Meaning, it should allow any
in-flight password hashing to complete, reject any new requests, respond with a 200 and
shutdown.

Test 1: Try a simple shut down while no requests are in progress
Test 2: Test shutdown with 1 request pending
Test 3: Test shutdown with many requests pending
Test 4: Test all 3 requests after shut down
'''


'''
Requirement 8: No additional password requests should be allowed when shutdown is pending.

curl -X POST -d 'shutdown' http://127.0.0.1:8765/hash > 
200 Empty Response

Test 1: Try shutting down while no password requests are pending and request a password
Test 2: Repeat test 1 with multiple requests
Test 3: Submit multiple password requests, shutdown, and make password requests both before and after shut down is complete

BUG: Only 1 password after shutdown is rejected. More than one request appear to be processed and it appears that the password hasher could be
     kept open indefinitely if password requests continue
'''
if __name__ == "__main__":
    # req_2_tests()
    req_3_tests()
    # test_ident_response_time()
    # test_base64_response_time()
    # req_4_tests()
    pprint.pprint(test_results)