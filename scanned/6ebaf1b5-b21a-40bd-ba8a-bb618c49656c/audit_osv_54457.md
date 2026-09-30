# [M] CVE-2023-6560

## Summary
Severity: Medium
Advisory: CVE-2023-6560
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-09
Source: https://osv.dev/vulnerability/CVE-2023-6560
Type: osv

## Details
An out-of-bounds memory access flaw was found in the io_uring SQ/CQ rings functionality in the Linux kernel. This issue could allow a local user to crash the system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AU4NHBDEDLRW33O76Y6LFECEYNQET5GZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UCQIPFUQXKXRCH5Y4RP3C5NK4IHNBNVK/
- http://packetstormsecurity.com/files/176405/io_uring-__io_uaddr_map-Dangerous-Multi-Page-Handling.html
- https://access.redhat.com/security/cve/CVE-2023-6560
- https://bugzilla.redhat.com/show_bug.cgi?id=2253249
- https://patchwork.kernel.org/project/io-uring/patch/20231130194633.649319-2-axboe@kernel.dk/
