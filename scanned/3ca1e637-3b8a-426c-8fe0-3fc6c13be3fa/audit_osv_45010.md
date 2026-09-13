# [H] LXD Snapshot Import Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-9640
Aliases: GHSA-ppq7-4492-5552
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-9640
Type: osv

## Details
A privilege escalation vulnerability exists in LXD from 6.0 before 6.9, 5.21.0 before 5.21.5, and 5.0.0 before 5.0.7 regarding the handling of project-restriction policies during snapshot restoration.. An authenticated project operator in a restricted multi-tenant environment can bypass policy restrictions by importing a maliciously crafted instance backup containing restricted configuration keys within a snapshot. When the snapshot is restored, these restricted keys are applied to the live instance without policy validation. Starting the modified instance grants the operator unauthorized host root access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9640.json
- https://github.com/canonical/lxd/security/advisories/GHSA-ppq7-4492-5552
- https://nvd.nist.gov/vuln/detail/CVE-2026-9640
- https://github.com/canonical/lxd/pull/18301
- https://github.com/canonical/lxd/pull/18303
- https://github.com/canonical/lxd/pull/18304
- https://github.com/canonical/lxd
