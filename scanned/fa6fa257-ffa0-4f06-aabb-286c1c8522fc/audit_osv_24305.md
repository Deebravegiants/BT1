# [M] CVE-2023-0394

## Summary
Severity: Medium
Advisory: CVE-2023-0394
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-24
Source: https://osv.dev/vulnerability/CVE-2023-0394
Type: osv

## Details
A NULL pointer dereference flaw was found in rawv6_push_pending_frames in net/ipv6/raw.c in the network subcomponent in the Linux kernel. This flaw causes the system to crash.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cb3e9864cdbe35ff6378966660edbcbac955fe17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0394.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0394
- https://security.netapp.com/advisory/ntap-20230302-0005/
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
