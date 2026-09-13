# [M] Deserialization of Untrusted Data in logback

## Summary
Severity: Medium
Advisory: GHSA-668q-qrv7-99fm
CVE: CVE-2021-42550
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-17
Source: https://github.com/advisories/GHSA-668q-qrv7-99fm
Type: github-advisory

## Affected
- Maven: `ch.qos.logback:logback-core` — affected >=0 <1.2.9

## Details
In logback version 1.2.7 and prior versions, an attacker with the required privileges to edit configurations files could craft a malicious configuration allowing to execute arbitrary code loaded from LDAP servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42550
- https://github.com/qos-ch/logback/commit/87291079a1de9369ac67e20dc70a8fdc7cc4359c
- https://github.com/qos-ch/logback/commit/ef4fc4186b74b45ce80d86833820106ff27edd42
- https://cert-portal.siemens.com/productcert/pdf/ssa-371761.pdf
- https://github.com/cn-panda/logbackRceDemo
- https://github.com/qos-ch/logback
- https://github.com/qos-ch/logback/blob/1502cba4c1dfd135b2e715bc0cf80c0045d4d128/logback-site/src/site/pages/news.html
- https://jira.qos.ch/browse/LOGBACK-1591
- https://security.netapp.com/advisory/ntap-20211229-0001
- http://logback.qos.ch/news.html
- http://packetstormsecurity.com/files/167794/Open-Xchange-App-Suite-7.10.x-Cross-Site-Scripting-Command-Injection.html
- http://seclists.org/fulldisclosure/2022/Jul/11
