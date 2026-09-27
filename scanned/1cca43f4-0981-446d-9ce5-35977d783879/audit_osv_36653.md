# [C] OpenEMR Arbitrary File Write leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-24848
Aliases: GHSA-5vp5-4rm6-h4c9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-24848
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. In 7.0.4 and earlier, the disposeDocument() method in EtherFaxActions.php allows authenticated users to write arbitrary content to arbitrary locations on the server filesystem. This vulnerability can be exploited to achieve Remote Code Execution (RCE) by uploading malicious PHP web shells.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24848.json
- https://github.com/openemr/openemr/security/advisories/GHSA-5vp5-4rm6-h4c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24848
