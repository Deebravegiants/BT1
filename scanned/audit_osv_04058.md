# [M] BIT-apache-2020-1927

## Summary
Severity: Medium
Advisory: BIT-apache-2020-1927
Aliases: CVE-2020-1927
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2020-1927
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.42

## Details
In Apache HTTP Server 2.4.0 to 2.4.41, redirects configured with mod_rewrite that were intended to be self-referential might be fooled by encoded newlines and redirect instead to an an unexpected URL within the request URL.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00002.html
- http://www.openwall.com/lists/oss-security/2020/04/03/1
- http://www.openwall.com/lists/oss-security/2020/04/04/1
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.apache.org/thread.html/r06f0d87ebb6d59ed8379633f36f72f5b1f79cadfda72ede0830b42cf%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r09bb998baee74a2c316446bd1a41ae7f8d7049d09d9ff991471e8775%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r10b853ea87dd150b0e76fda3f8254dfdb23dd05fa55596405b58478e%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r1719675306dfbeaceff3dc63ccad3de2d5615919ca3c13276948b9ac%40%3Cdev.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r3c5c3104813c1c5508b55564b66546933079250a46ce50eee90b2e36%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r52a52fd60a258f5999a8fa5424b30d9fd795885f9ff4828d889cd201%40%3Cdev.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r6a4146bf3d1645af2880f8b7a4fd8afd696d5fd4a3ae272f49f5dc84%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r70ba652b79ba224b2cbc0a183078b3a49df783b419903e3dcf4d78c7%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r731d43caece41d78d8c6304641a02a369fd78300e7ffaf566b06bc59%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r76142b8c5119df2178be7c2dba88fde552eedeec37ea993dfce68d1d%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/r9f93cf6dde308d42a9c807784e8102600d0397f5f834890708bf6920%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rc998b18880df98bafaade071346690c2bc1444adaa1a1ea464b93f0a%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rdf3e5d0a5f5c3d90d6013bccc6c4d5af59cf1f8c8dea5d9a283d13ce%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/rf6449464fd8b7437704c55f88361b66f12d5b5f90bcce66af4be4ba9%40%3Ccvs.httpd.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/07/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A2RN46PRBJE7E7OPD4YZX5SVWV5QKGV5/
