# [H] CVE-2026-41292

## Summary
Severity: High
Advisory: CVE-2026-41292
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-41292
Type: osv

## Details
NLnet Labs Unbound up to and including version 1.25.0 is vulnerable to a degradation of service attack related to parsing long lists of incoming EDNS options. An adversary sending queries with too many EDNS options can hold Unbound threads hostage while they are parsing and creating internal data structures for the options. Coordinated attacks can result in degradation and/or denial of service. Unbound 1.25.1 contains a patch with a fix to limit acceptable incoming EDNS options (100).

## References
- https://access.redhat.com/security/cve/CVE-2026-41292
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41292.json
- https://access.redhat.com/errata/RHSA-2026:24013
- https://access.redhat.com/errata/RHSA-2026:36320
- https://access.redhat.com/errata/RHSA-2026:36777
- https://access.redhat.com/errata/RHSA-2026:37282
- https://access.redhat.com/errata/RHSA-2026:54769
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-41292.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2480125
