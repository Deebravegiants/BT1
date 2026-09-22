# [H] Request splitting via HTTP/2 method injection and mod_proxy

## Summary
Severity: High
Advisory: BIT-apache-2021-33193
Aliases: CVE-2021-33193
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2021-33193
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.17 <2.4.49

## Details
A crafted method sent through HTTP/2 will bypass validation and be forwarded by mod_proxy, which can lead to request splitting or cache poisoning. This issue affects Apache HTTP Server 2.4.17 to 2.4.48.

## References
- https://github.com/apache/httpd/commit/ecebcc035ccd8d0e2984fe41420d9e944f456b3c.patch
- https://lists.apache.org/thread.html/re4162adc051c1a0a79e7a24093f3776373e8733abaff57253fef341d%40%3Ccvs.httpd.apache.org%3E
- https://lists.apache.org/thread.html/ree7519d71415ecdd170ff1889cab552d71758d2ba2904a17ded21a70%40%3Ccvs.httpd.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2023/03/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DSM6UWQICBJ2TU727RENU3HBKEAFLT6T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EUVJVRJRBW5QVX4OY3NOHZDQ3B3YOTSG/
- https://portswigger.net/research/http2
- https://security.gentoo.org/glsa/202208-20
- https://security.netapp.com/advisory/ntap-20210917-0004/
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-httpd-2.4.49-VWL69sWQ
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.tenable.com/security/tns-2021-17
- https://nvd.nist.gov/vuln/detail/CVE-2021-33193
