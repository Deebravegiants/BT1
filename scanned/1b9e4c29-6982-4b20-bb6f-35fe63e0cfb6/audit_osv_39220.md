# [M] OFFIS DCMTK Toolkit Type Confusion

## Summary
Severity: Medium
Advisory: CVE-2026-44628
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-44628
Type: osv

## Details
An unauthenticated attacker can crash the worklist server with a single crafted query when the server has a valid Called AE Title / storage directory, the expected lockfile, and at least one matching worklist record.

## References
- https://github.com/DCMTK/dcmtk/releases/tag/latest
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsma-26-181-01.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44628.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44628
- https://www.cisa.gov/news-events/ics-medical-advisories/icsma-26-181-01
