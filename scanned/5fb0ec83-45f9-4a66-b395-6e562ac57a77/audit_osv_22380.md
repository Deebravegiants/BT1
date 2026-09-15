# [H] CVE-2022-27925

## Summary
Severity: High
Advisory: CVE-2022-27925
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-20
Source: https://osv.dev/vulnerability/CVE-2022-27925
Type: osv

## Details
Zimbra Collaboration (aka ZCS) 8.8.15 and 9.0 has mboximport functionality that receives a ZIP archive and extracts files from it. An authenticated user with administrator rights has the ability to upload arbitrary files to the system, leading to directory traversal.

## References
- http://packetstormsecurity.com/files/168146/Zimbra-Zip-Path-Traversal.html
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P24
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-27925
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/27xxx/CVE-2022-27925.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-27925
