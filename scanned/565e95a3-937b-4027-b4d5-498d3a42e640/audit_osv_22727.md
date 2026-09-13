# [C] CVE-2022-37042

## Summary
Severity: Critical
Advisory: CVE-2022-37042
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-11
Source: https://osv.dev/vulnerability/CVE-2022-37042
Type: osv

## Details
Zimbra Collaboration Suite (ZCS) 8.8.15 and 9.0 has mboximport functionality that receives a ZIP archive and extracts files from it. By bypassing authentication (i.e., not having an authtoken), an attacker can upload arbitrary files to the system, leading to directory traversal and remote code execution. NOTE: this issue exists because of an incomplete fix for CVE-2022-27925.

## References
- http://packetstormsecurity.com/files/168146/Zimbra-Zip-Path-Traversal.html
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-37042
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37042.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37042
