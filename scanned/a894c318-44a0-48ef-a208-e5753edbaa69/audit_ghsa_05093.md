# [C] golang.org/x/crypto: Invoking client can cause server deadlock on unexpected responses

## Summary
Severity: Critical
Advisory: GHSA-vgwf-h737-ff37
CVE: CVE-2026-39830
CWE: CWE-119, CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-vgwf-h737-ff37
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
A malicious SSH peer could send unsolicited global request responses to fill an internal buffer, blocking the connection's read loop. The blocked goroutine could not be released by calling Close(), resulting in a resource leak per connection. Unsolicited global responses are now discarded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39830
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/errata/RHSA-2026:42146
- https://access.redhat.com/errata/RHSA-2026:42796
- https://access.redhat.com/errata/RHSA-2026:43052
- https://access.redhat.com/errata/RHSA-2026:43692
- https://access.redhat.com/errata/RHSA-2026:46885
- https://access.redhat.com/errata/RHSA-2026:47735
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:49944
- https://access.redhat.com/errata/RHSA-2026:51033
- https://access.redhat.com/errata/RHSA-2026:52857
- https://access.redhat.com/errata/RHSA-2026:52910
- https://access.redhat.com/errata/RHSA-2026:54400
- https://access.redhat.com/errata/RHSA-2026:54531
- https://access.redhat.com/errata/RHSA-2026:57194
- https://access.redhat.com/errata/RHSA-2026:57801
- https://access.redhat.com/errata/RHSA-2026:59467
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/errata/RHSA-2026:61314
