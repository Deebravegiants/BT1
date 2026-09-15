# [M] DNN allows the possibility of bypassing Captcha

## Summary
Severity: Medium
Advisory: CVE-2025-32036
Aliases: GHSA-48q9-3p26-8595
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-32036
Type: osv

## Details
DNN (formerly DotNetNuke) is an open-source web content management platform (CMS) in the Microsoft ecosystem. The algorithm used to generate the captcha image shows the least complexity of the desired image. For this reason, the created image can be easily read by OCR tools, and the intruder can send automatic requests by building a robot and using this tool. This vulnerability is fixed in 9.13.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32036.json
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-48q9-3p26-8595
- https://nvd.nist.gov/vuln/detail/CVE-2025-32036
- https://github.com/dnnsoftware/Dnn.Platform/commit/abda726e75f1938c8d89795b5dceb80dc4e2e6c5
