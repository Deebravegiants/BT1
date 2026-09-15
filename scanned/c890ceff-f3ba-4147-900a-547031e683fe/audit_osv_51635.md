# [M] CVE-2021-3714

## Summary
Severity: Medium
Advisory: CVE-2021-3714
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3714
Type: osv

## Details
A flaw was found in the Linux kernels memory deduplication mechanism. Previous work has shown that memory deduplication can be attacked via a local exploitation mechanism. The same technique can be used if an attacker can upload page sized files and detect the change in access time from a networked service to determine if the page has been merged.

## References
- https://access.redhat.com/security/cve/CVE-2021-3714
- https://arxiv.org/abs/2111.08553
- https://arxiv.org/pdf/2111.08553.pdf
- https://bugzilla.redhat.com/show_bug.cgi?id=1931327
