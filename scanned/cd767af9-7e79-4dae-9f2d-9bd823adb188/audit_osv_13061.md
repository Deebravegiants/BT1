# [M] CVE-2018-17189

## Summary
Severity: Medium
Advisory: CVE-2018-17189
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-01-30
Source: https://osv.dev/vulnerability/CVE-2018-17189
Type: osv

## Details
In Apache HTTP server versions 2.4.37 and prior, by sending request bodies in a slow loris way to plain resources, the h2 stream for that request unnecessarily occupied a server thread cleaning up that incoming data. This affects only HTTP/2 (mod_http2) connections.

## References
- https://lists.apache.org/thread.html/56c2e7cc9deb1c12a843d0dc251ea7fd3e7e80293cde02fcd65286ba%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/84a3714f0878781f6ed84473d1a503d2cc382277e100450209231830%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r06f0d87ebb6d59ed8379633f36f72f5b1f79cadfda72ede0830b42cf%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r15f9aa4427581a1aecb4063f1b4b983511ae1c9935e2a0a6876dad3c%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r76142b8c5119df2178be7c2dba88fde552eedeec37ea993dfce68d1d%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9f93cf6dde308d42a9c807784e8102600d0397f5f834890708bf6920%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rc998b18880df98bafaade071346690c2bc1444adaa1a1ea464b93f0a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd18c3c43602e66f9cdcf09f1de233804975b9572b0456cc582390b6f%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rd2fb621142e7fa187cfe12d7137bf66e7234abcbbcd800074c84a538%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re3d27b6250aa8548b8845d314bb8a350b3df326cacbbfdfe4d455234%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/re473305a65b4db888e3556e4dae10c2a04ee89dcff2e26ecdbd860a9%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rf6449464fd8b7437704c55f88361b66f12d5b5f90bcce66af4be4ba9%40%3Ccvs.httpd.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IY7SJQOO3PYFVINZW6H5EK4EZ3HSGZNM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U7N3DUEBFVGQWQEME5HTPTTKDHGHBAC6/
- http://www.securityfocus.com/bid/106685
- https://access.redhat.com/errata/RHSA-2019:3932
- https://access.redhat.com/errata/RHSA-2019:3933
- https://access.redhat.com/errata/RHSA-2019:3935
- https://access.redhat.com/errata/RHSA-2019:4126
- https://httpd.apache.org/security/vulnerabilities_24.html
