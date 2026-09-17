# [M] golang.org/x/crypto is vulnerable to invoking server panic during CheckHostKey/Authenticate flow

## Summary
Severity: Medium
Advisory: GHSA-78mq-xcr3-xm33
CVE: CVE-2026-39835
CWE: CWE-295, CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-78mq-xcr3-xm33
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
SSH servers which use CertChecker as a public key callback without setting IsUserAuthority or IsHostAuthority could be caused to panic by a client presenting a certificate. CertChecker now returns an error instead of panicking when these callbacks are nil.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39835
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/errata/RHSA-2026:42146
- https://access.redhat.com/errata/RHSA-2026:42796
- https://access.redhat.com/errata/RHSA-2026:43052
- https://access.redhat.com/errata/RHSA-2026:43692
- https://access.redhat.com/errata/RHSA-2026:46885
- https://access.redhat.com/errata/RHSA-2026:47735
- https://access.redhat.com/errata/RHSA-2026:47949
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:51033
- https://access.redhat.com/errata/RHSA-2026:51036
- https://access.redhat.com/errata/RHSA-2026:51038
- https://access.redhat.com/errata/RHSA-2026:52857
- https://access.redhat.com/errata/RHSA-2026:52910
- https://access.redhat.com/errata/RHSA-2026:54525
- https://access.redhat.com/errata/RHSA-2026:57194
- https://access.redhat.com/errata/RHSA-2026:59467
- https://access.redhat.com/errata/RHSA-2026:59593
- https://access.redhat.com/errata/RHSA-2026:60520
