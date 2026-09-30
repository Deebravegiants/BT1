# [M] Local file inclusion allows unauthorized access to internal resources in Alkacon OpenCms

## Summary
Severity: Medium
Advisory: GHSA-36hf-6hp2-9g4c
CVE: CVE-2019-13237
CWE: CWE-200, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-36hf-6hp2-9g4c
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <11.0.1

## Details
In Alkacon OpenCms 10.5.4 and 10.5.5, there are multiple resources vulnerable to Local File Inclusion that allow an attacker to access server resources: clearhistory.jsp, convertxml.jsp, group_new.jsp, loginmessage.jsp, xmlcontentrepair.jsp, and /system/workplace/admin/history/settings/index.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13237
- https://aetsu.github.io/OpenCms
- https://github.com/alkacon/opencms-core
- https://github.com/alkacon/opencms-core/commits/branch_10_5_x
- http://packetstormsecurity.com/files/154281/Alkacon-OpenCMS-10.5.x-Local-File-Inclusion.html
