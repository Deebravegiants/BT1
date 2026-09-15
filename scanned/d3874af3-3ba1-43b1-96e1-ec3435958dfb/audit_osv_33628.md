# [M] Emlog vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: CVE-2025-47784
Aliases: GHSA-f56g-m99v-mqc3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-47784
Type: osv

## Details
Emlog is an open source website building system. Versions 2.5.13 and prior have a deserialization vulnerability. A user who creates a carefully crafted nickname can cause `str_replace` to replace the value of `name_orig` with empty, causing deserialization to fail and return `false`. Commit 9643250802188b791419e3c2188577073256a8a2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47784.json
- https://github.com/emlog/emlog/security/advisories/GHSA-f56g-m99v-mqc3
- https://nvd.nist.gov/vuln/detail/CVE-2025-47784
- https://github.com/emlog/emlog/commit/9643250802188b791419e3c2188577073256a8a2
