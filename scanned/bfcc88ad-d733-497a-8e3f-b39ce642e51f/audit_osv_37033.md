# [H] CVE-2026-27858

## Summary
Severity: High
Advisory: CVE-2026-27858
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-27858
Type: osv

## Details
Attacker can send a specifically crafted message before authentication that causes managesieve to allocate large amount of memory.
 Attacker can force managesieve-login to be unavailable by repeatedly crashing the process. Protect access to managesieve protocol, or install fixed version. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27858.json
- https://access.redhat.com/errata/RHSA-2026:13498
- https://access.redhat.com/errata/RHSA-2026:13830
- https://access.redhat.com/errata/RHSA-2026:13857
- https://access.redhat.com/errata/RHSA-2026:17602
- https://access.redhat.com/errata/RHSA-2026:17625
- https://access.redhat.com/errata/RHSA-2026:17626
- https://access.redhat.com/errata/RHSA-2026:17628
- https://access.redhat.com/errata/RHSA-2026:17630
- https://access.redhat.com/errata/RHSA-2026:18053
- https://access.redhat.com/errata/RHSA-2026:19149
- https://access.redhat.com/errata/RHSA-2026:19364
- https://access.redhat.com/errata/RHSA-2026:19453
- https://access.redhat.com/errata/RHSA-2026:19455
- https://access.redhat.com/errata/RHSA-2026:26564
- https://access.redhat.com/security/cve/CVE-2026-27858
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27858.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27858
- https://bugzilla.redhat.com/show_bug.cgi?id=2452175
