# [C] Grav CMS before 2.0.13 Remote Code Execution via ZIP Upload

## Summary
Severity: Critical
Advisory: CVE-2026-72819
Aliases: GHSA-r94f-hx44-8jqf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72819
Type: osv

## Details
Grav CMS before 2.0.13 contains a remote code execution vulnerability in the Flex Objects plugin settings validation that allows authenticated users to execute arbitrary code by uploading a ZIP file containing PHP code. Attackers can bypass routine name validation by using array notation instead of string notation, call the unZip routine with a malicious archive, and write PHP files to the web root for execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72819.json
- https://github.com/getgrav/grav/security/advisories/GHSA-r94f-hx44-8jqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-72819
- https://www.vulncheck.com/advisories/grav-cms-before-remote-code-execution-via-zip-upload
