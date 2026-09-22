# [M] Xen Orchestra Mishandles Authorization

## Summary
Severity: Medium
Advisory: GHSA-grvm-gcqf-gh8q
CVE: CVE-2021-36383
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-grvm-gcqf-gh8q
Type: github-advisory

## Affected
- npm: `xo-web` — affected >=0
- npm: `xo-server` — affected >=0

## Details
Xen Orchestra (with xo-web through 5.80.0 and xo-server through 5.84.0) mishandles authorization, as demonstrated by modified WebSocket `resourceSet.getAll` data is which the attacker changes the permission field from none to admin. The attacker gains access to data sets such as VMs, Backups, Audit, Users, and Groups.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36383
- https://github.com/vatesfr/xen-orchestra/issues/5712
- https://github.com/vatesfr/xen-orchestra
