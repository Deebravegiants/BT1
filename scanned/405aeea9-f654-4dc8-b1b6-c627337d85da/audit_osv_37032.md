# [M] CVE-2026-27857

## Summary
Severity: Medium
Advisory: CVE-2026-27857
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-27857
Type: osv

## Details
Sending "NOOP (((...)))" command with 4000 parenthesis open+close results in ~1MB extra memory usage. Longer commands will result in client disconnection. This 1 MB can be left allocated for longer time periods by not sending the command ending LF. So attacker could connect possibly from even a single IP and create 1000 connections to allocate 1 GB of memory, which would likely result in reaching VSZ limit and killing the process and its other proxied connections. Attacker could connect possibly from even a single IP and create 1000 connections to allocate 1 GB of memory, which would likely result in reaching VSZ limit and killing the process and its other proxied connections. Install fixed version, there is no other remediation. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27857.json
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
- https://access.redhat.com/security/cve/CVE-2026-27857
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27857.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27857
- https://bugzilla.redhat.com/show_bug.cgi?id=2452179
