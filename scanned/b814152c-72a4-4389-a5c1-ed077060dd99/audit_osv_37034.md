# [M] CVE-2026-27859

## Summary
Severity: Medium
Advisory: CVE-2026-27859
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-27859
Type: osv

## Details
A mail message containing excessive amount of RFC 2231 MIME parameters causes LMTP to use too much CPU. A suitably formatted mail message causes mail delivery process to consume large amounts of CPU time. Use MTA capabilities to limit RFC 2231 MIME parameters in mail messages, or upgrade to fixed version where the processing is limited. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27859.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27859
