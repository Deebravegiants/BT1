# [H] Rancher: SAML Assertion Replay

## Summary
Severity: High
Advisory: CVE-2026-75034
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-75034
Type: osv

## Details
A flaw was found in Rancher Manager. The SAML assertion replay protection introduced by the fix for CVE-2026-44946 recorded consumed assertion IDs in a per-process cache, so each replica only detected replays that reached the same pod. In a high-availability deployment, an attacker holding a captured assertion could replay it once against every other replica to obtain additional authenticated sessions as the victim.


This issue affects Rancher: before 2.15.1.

## References
- https://github.com/rancher/rancher/releases/tag/v2.15.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75034
- https://github.com/rancher/rancher
