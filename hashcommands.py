import requests, os, random, time, subprocess

def start(port_type):
    try:
        if port_type is None:
            port = None
            print('Port set to None')
            subprocess.Popen('JumpCloud/broken-hashserve_darwin')
            return None
        else:
            if port_type is 'random':
                # Set a random port above 1080 to avoid common port numbers
                port = str(random.randint(1081, 65535))
            elif port_type is 8088:
                port = '8088'
            elif port_type is None:
                port = None
            else:
                print('Port not specified, setting port to 8088')
                port = '8088'
            if port is not None:
                os.environ['PORT'] = port
            print('Port set to ' + port)
            subprocess.Popen('JumpCloud/broken-hashserve_darwin')
            return port
    except:
        print('Start hashserve failed')

def submit_password(password):
    response = requests.post('http://127.0.0.1:' + port + '/hash', '{"password":"' + password + '"}')
    print(response.elapsed.seconds)
    return response.text

def stats(job_ident):
    response = requests.get('http://127.0.0.1:' + port + '/stats')
    print(response.elapsed.seconds)
    return response.text

def stop(port):
    try:
        if port is None:
            print('Sending shut down post on None port')
            requests.post('http://127.0.0.1:/hash', 'shutdown')
        else:
            print('Sending shut down post on port ' + port)
        requests.post('http://127.0.0.1:' + port + '/hash', 'shutdown')
    except Exception as exc:
        if str(exc) == '(\'Connection aborted.\', RemoteDisconnected(\'Remote end closed connection without response\'))':
            print('Shut down successful')
        else:
            print('Shutting down hash program may have failed, unexpected expetion:')
            print(exc)