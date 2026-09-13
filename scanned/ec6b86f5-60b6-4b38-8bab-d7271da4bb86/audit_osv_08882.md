# [H] CVE-2016-6560

## Summary
Severity: High
Advisory: CVE-2016-6560
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-31
Source: https://osv.dev/vulnerability/CVE-2016-6560
Type: osv

## Details
illumos osnet-incorporation bcopy() and bzero() implementations make signed instead of unsigned comparisons allowing a system crash.

## References
- https://www.openindiana.org/2016/11/01/cve-2016-6560-cve-2016-6561-security-issues-in-illumos/
- https://www.illumos.org/issues/7488
- https://github.com/illumos/illumos-gate/commit/5aaab1a49679c26dbcb6fb6dc25799950d70cc71
