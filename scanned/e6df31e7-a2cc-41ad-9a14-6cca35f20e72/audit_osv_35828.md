# [H] CVE-2026-1519

## Summary
Severity: High
Advisory: CVE-2026-1519
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-1519
Type: osv

## Details
If a BIND resolver is performing DNSSEC validation and encounters a maliciously crafted zone, the resolver may consume excessive CPU. Authoritative-only servers are generally unaffected, although there are circumstances where authoritative servers may make recursive queries (see: https://kb.isc.org/docs/why-does-my-authoritative-server-make-recursive-queries).
This issue affects BIND 9 versions 9.11.0 through 9.16.50, 9.18.0 through 9.18.46, 9.20.0 through 9.20.20, 9.21.0 through 9.21.19, 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.46-S1, and 9.20.9-S1 through 9.20.20-S1.

## References
- https://access.redhat.com/security/cve/CVE-2026-1519
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1519.json
- https://access.redhat.com/errata/RHSA-2026:11371
- https://access.redhat.com/errata/RHSA-2026:11372
- https://access.redhat.com/errata/RHSA-2026:15890
- https://access.redhat.com/errata/RHSA-2026:16060
- https://access.redhat.com/errata/RHSA-2026:16064
- https://access.redhat.com/errata/RHSA-2026:24500
- https://access.redhat.com/errata/RHSA-2026:24851
- https://access.redhat.com/errata/RHSA-2026:24934
- https://access.redhat.com/errata/RHSA-2026:25083
- https://access.redhat.com/errata/RHSA-2026:25171
- https://access.redhat.com/errata/RHSA-2026:25214
- https://access.redhat.com/errata/RHSA-2026:29110
- https://access.redhat.com/errata/RHSA-2026:29863
- https://access.redhat.com/errata/RHSA-2026:34048
- https://access.redhat.com/errata/RHSA-2026:36610
- https://access.redhat.com/errata/RHSA-2026:40021
- https://access.redhat.com/errata/RHSA-2026:43226
- https://access.redhat.com/errata/RHSA-2026:60019
