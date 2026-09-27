# [C] CVE-2020-14315

## Summary
Severity: Critical
Advisory: CVE-2020-14315
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-14315
Type: osv

## Details
A memory corruption vulnerability is present in bspatch as shipped in Colin Percival’s bsdiff tools version 4.3. Insufficient checks when handling external inputs allows an attacker to bypass the sanity checks in place and write out of a dynamically allocated buffer boundaries.

## References
- https://www.openwall.com/lists/oss-security/2020/07/09/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1856747
- https://www.x41-dsec.de/lab/advisories/x41-2020-006-bspatch/
