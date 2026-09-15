# [M] OFFIS DCMTK Toolkit Missing Release of Memory after Effective Lifetime

## Summary
Severity: Medium
Advisory: CVE-2026-35505
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-35505
Type: osv

## Details
An unauthenticated remote attacker can repeatedly send crafted connection requests to leak memory. In single-process deployments the memory grows until the service is killed and the port stops responding until restart.

## References
- https://github.com/DCMTK/dcmtk/releases/tag/latest
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsma-26-181-01.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35505.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35505
- https://www.cisa.gov/news-events/ics-medical-advisories/icsma-26-181-01
