# [H] CVE-2025-59032

## Summary
Severity: High
Advisory: CVE-2025-59032
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2025-59032
Type: osv

## Details
ManageSieve AUTHENTICATE command crashes when using literal as SASL initial response. This can be used to crash ManageSieve service repeatedly, making it unavailable for other users. Control access to ManageSieve port, or disable the service if it's not needed. Alternatively upgrade to a fixed version. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-59032.json
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
- https://access.redhat.com/security/cve/CVE-2025-59032
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59032.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59032
- https://bugzilla.redhat.com/show_bug.cgi?id=2452172
