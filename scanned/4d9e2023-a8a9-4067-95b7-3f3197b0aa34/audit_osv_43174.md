# [H] OpenSignLabs opensignserver - Missing Authorization

## Summary
Severity: High
Advisory: CVE-2026-72692
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72692
Type: osv

## Details
A missing authorization vulnerability in OpenSignLabs opensignserver through 2.37.0 allows an unauthenticated remote attacker to irreversibly decline any in-flight document and forge the decline attribution to an arbitrary user via the declinedoc Parse cloud function. The function writes IsDeclined, DeclineReason, and a caller-supplied DeclineBy pointer without verifying the caller's identity, enabling workflow termination and evidentiary record falsification against any accessible document.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72692.json
- https://github.com/OpenSignLabs/OpenSign
- https://nvd.nist.gov/vuln/detail/CVE-2026-72692
