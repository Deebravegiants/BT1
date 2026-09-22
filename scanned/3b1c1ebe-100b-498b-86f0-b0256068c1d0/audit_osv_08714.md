# [H] CVE-2016-5387

## Summary
Severity: High
Advisory: CVE-2016-5387
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-19
Source: https://osv.dev/vulnerability/CVE-2016-5387
Type: osv

## Details
The Apache HTTP Server through 2.4.23 follows RFC 3875 section 4.1.18 and therefore does not protect applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect an application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an "httpoxy" issue.  NOTE: the vendor states "This mitigation has been assigned the identifier CVE-2016-5387"; in other words, this is not a CVE ID for a vulnerability.

## References
- https://lists.apache.org/thread.html/56c2e7cc9deb1c12a843d0dc251ea7fd3e7e80293cde02fcd65286ba%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/84a3714f0878781f6ed84473d1a503d2cc382277e100450209231830%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/8d63cb8e9100f28a99429b4328e4e7cebce861d5772ac9863ba2ae6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/f7f95ac1cd9895db2714fa3ebaa0b94d0c6df360f742a40951384a53%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r04e89e873d54116a0635ef2f7061c15acc5ed27ef7500997beb65d6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r476d175be0aaf4a17680ef98c5153b4d336eaef76fb2224cc94c463a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r57608dc51b79102f3952ae06f54d5277b649c86d6533dcd6a7d201f7%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r75cbe9ea3e2114e4271bbeca7aff96117b50c1b6eb7c4772b0337c1f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9ea3538f229874c80a10af473856a81fbf5f694cd7f471cc679ba70b%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9f93cf6dde308d42a9c807784e8102600d0397f5f834890708bf6920%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rad01d817195e6cc871cb1d73b207ca326379a20a6e7f30febaf56d24%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rb14daf9cc4e28d18cdc15d6a6ca74e565672fabf7ad89541071d008b%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rc998b18880df98bafaade071346690c2bc1444adaa1a1ea464b93f0a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rcc44594d4d6579b90deccd4536b5d31f099ef563df39b094be286b9e%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd18c3c43602e66f9cdcf09f1de233804975b9572b0456cc582390b6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd336919f655b7ff309385e34a143e41c503e133da80414485b3abcc9%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rdca61ae990660bacb682295f2a09d34612b7bb5f457577fe17f4d064%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re1e3a24664d35bcd0a0e793e0b5fc6ca6c107f99a1b2c545c5d4b467%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re3d27b6250aa8548b8845d314bb8a350b3df326cacbbfdfe4d455234%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rf6449464fd8b7437704c55f88361b66f12d5b5f90bcce66af4be4ba9%40%3Ccvs.httpd.apache.org%3E
