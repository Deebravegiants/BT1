# [M] CVE-2025-4877

## Summary
Severity: Medium
Advisory: CVE-2025-4877
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-08-20
Source: https://osv.dev/vulnerability/CVE-2025-4877
Type: osv

## Details
There's a vulnerability in the libssh package where when a libssh consumer passes in an unexpectedly large input buffer to ssh_get_fingerprint_hash() function. In such cases the bin_to_base64() function can experience an integer overflow leading to a memory under allocation, when that happens it's possible that the program perform out of bounds write leading to a heap corruption.
This issue affects only 32-bits builds of libssh.

## References
- https://www.libssh.org/security/advisories/CVE-2025-4877.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2376193
- https://access.redhat.com/security/cve/CVE-2025-4877
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=6fd9cc8ce3958092a1aae11f1f2e911b2747732d
