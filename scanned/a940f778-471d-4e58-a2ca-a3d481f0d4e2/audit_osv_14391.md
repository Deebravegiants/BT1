# [M] CVE-2019-0220

## Summary
Severity: Medium
Advisory: CVE-2019-0220
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/CVE-2019-0220
Type: osv

## Details
A vulnerability was found in Apache HTTP Server 2.4.0 to 2.4.38. When the path component of a request URL contains multiple consecutive slashes ('/'), directives such as LocationMatch and RewriteRule must account for duplicates in regular expressions while other aspects of the servers processing will implicitly collapse them.

## References
- https://lists.apache.org/thread.html/56c2e7cc9deb1c12a843d0dc251ea7fd3e7e80293cde02fcd65286ba%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/84a3714f0878781f6ed84473d1a503d2cc382277e100450209231830%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r03ee478b3dda3e381fd6189366fa7af97c980d2f602846eef935277d%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r06f0d87ebb6d59ed8379633f36f72f5b1f79cadfda72ede0830b42cf%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r31f46d1f16ffcafa68058596b21f6eaf6d352290e522690a1cdccdd7%40%3Cbugs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r76142b8c5119df2178be7c2dba88fde552eedeec37ea993dfce68d1d%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9f93cf6dde308d42a9c807784e8102600d0397f5f834890708bf6920%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rc998b18880df98bafaade071346690c2bc1444adaa1a1ea464b93f0a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd18c3c43602e66f9cdcf09f1de233804975b9572b0456cc582390b6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd2fb621142e7fa187cfe12d7137bf66e7234abcbbcd800074c84a538%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd336919f655b7ff309385e34a143e41c503e133da80414485b3abcc9%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re3d27b6250aa8548b8845d314bb8a350b3df326cacbbfdfe4d455234%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re473305a65b4db888e3556e4dae10c2a04ee89dcff2e26ecdbd860a9%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rf6449464fd8b7437704c55f88361b66f12d5b5f90bcce66af4be4ba9%40%3Ccvs.httpd.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ALIR5S3O7NRHEGFMIDMUSYQIZOE4TJJN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZRMTEIGZKYFNGIDOTXN3GNEJTLVCYU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WETXNQWNQLWHV6XNW6YTO5UGDTIWAQGT/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03950en_us
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
