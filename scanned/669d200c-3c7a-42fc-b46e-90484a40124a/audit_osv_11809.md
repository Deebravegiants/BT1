# [H] CVE-2017-9798

## Summary
Severity: High
Advisory: CVE-2017-9798
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-18
Source: https://osv.dev/vulnerability/CVE-2017-9798
Type: osv

## Details
Apache httpd allows remote attackers to read secret data from process memory if the Limit directive can be set in a user's .htaccess file, or if httpd.conf has certain misconfigurations, aka Optionsbleed. This affects the Apache HTTP Server through 2.2.34 and 2.4.x through 2.4.27. The attacker sends an unauthenticated OPTIONS HTTP request when attempting to read secret data. This is a use-after-free issue and thus secret data is not always sent, and the specific data depends on many factors including configuration. Exploitation with .htaccess can be blocked with a patch to the ap_limit_section function in server/core.c.

## References
- http://seclists.org/fulldisclosure/2024/Sep/22
- https://lists.apache.org/thread.html/56c2e7cc9deb1c12a843d0dc251ea7fd3e7e80293cde02fcd65286ba%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/84a3714f0878781f6ed84473d1a503d2cc382277e100450209231830%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/8d63cb8e9100f28a99429b4328e4e7cebce861d5772ac9863ba2ae6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/f7f95ac1cd9895db2714fa3ebaa0b94d0c6df360f742a40951384a53%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r15f9aa4427581a1aecb4063f1b4b983511ae1c9935e2a0a6876dad3c%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r57608dc51b79102f3952ae06f54d5277b649c86d6533dcd6a7d201f7%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r6521a7f62276340eabdb3339b2aa9a38c5f59d978497a1f794af53be%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r75cbe9ea3e2114e4271bbeca7aff96117b50c1b6eb7c4772b0337c1f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9ea3538f229874c80a10af473856a81fbf5f694cd7f471cc679ba70b%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9f93cf6dde308d42a9c807784e8102600d0397f5f834890708bf6920%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rc998b18880df98bafaade071346690c2bc1444adaa1a1ea464b93f0a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rcc44594d4d6579b90deccd4536b5d31f099ef563df39b094be286b9e%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd18c3c43602e66f9cdcf09f1de233804975b9572b0456cc582390b6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rdca61ae990660bacb682295f2a09d34612b7bb5f457577fe17f4d064%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re3d27b6250aa8548b8845d314bb8a350b3df326cacbbfdfe4d455234%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rf6449464fd8b7437704c55f88361b66f12d5b5f90bcce66af4be4ba9%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rfbaf647d52c1cb843e726a0933f156366a806cead84fbd430951591b%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rfcf929bd33a6833e3f0c35eebdad70d5060665f9c4e17ea467c66770%40%3Ccvs.httpd.apache.org%3E
- http://openwall.com/lists/oss-security/2017/09/18/2
