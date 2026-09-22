# [C] OS Command Injection endpoint '/upload/init' parameter 'filename' (RCE) in DumpDrop

## Summary
Severity: Critical
Advisory: CVE-2025-24971
Aliases: GHSA-rx8m-jqm7-vcgp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-24971
Type: osv

## Details
DumpDrop is a stupid simple file upload application that provides an interface for dragging and dropping files. An OS Command Injection vulnerability was discovered in the DumbDrop application, `/upload/init` endpoint. This vulnerability could allow an attacker to execute arbitrary code remotely when the **Apprise Notification** enabled. This issue has been addressed in commit `4ff8469d` and all users are advised to patch. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24971.json
- https://github.com/DumbWareio/DumbDrop/security/advisories/GHSA-rx8m-jqm7-vcgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-24971
- https://github.com/DumbWareio/DumbDrop/commit/4ff8469d69019d200046a67d326f51703bc4da63
