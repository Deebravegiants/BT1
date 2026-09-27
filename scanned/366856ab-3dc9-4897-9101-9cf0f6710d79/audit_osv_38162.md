# [M] ChangeDetection.io < 0.54.7 SafeXPath3Parser Bypass Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-35000
Aliases: PYSEC-2026-2131
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-35000
Type: osv

## Details
ChangeDetection.io versions prior to 0.54.7 contain a protection bypass vulnerability in the SafeXPath3Parser implementation that allows attackers to read arbitrary local files by using unblocked XPath 3.0/3.1 functions such as json-doc() and similar file-access primitives. Attackers can exploit the incomplete blocklist of dangerous XPath functions to access sensitive data from the local filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35000.json
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.54.7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35000
- https://www.vulncheck.com/advisories/changedetection-io-safexpath3parser-bypass-arbitrary-file-read
- https://github.com/dgtlmoon/changedetection.io/commit/dadc804567a51f803cd6715f7885c11a247915f6
- https://github.com/dgtlmoon/changedetection.io
