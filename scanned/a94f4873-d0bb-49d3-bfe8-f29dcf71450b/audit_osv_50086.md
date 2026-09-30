# [M] CVE-2019-7308

## Summary
Severity: Medium
Advisory: CVE-2019-7308
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-02-01
Source: https://osv.dev/vulnerability/CVE-2019-7308
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel before 4.20.6 performs undesirable out-of-bounds speculation on pointer arithmetic in various cases, including cases of different branches with different state or limits to sanitize, leading to side-channel attacks.

## References
- https://support.f5.com/csp/article/K43030517?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K43030517
- https://usn.ubuntu.com/3930-2/
- https://usn.ubuntu.com/3931-1/
- https://usn.ubuntu.com/3931-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00052.html
- http://www.securityfocus.com/bid/106827
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.6
- https://usn.ubuntu.com/3930-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=979d63d50c0c0f7bc537bf821e056cc9fe5abd38
- https://github.com/torvalds/linux/commit/979d63d50c0c0f7bc537bf821e056cc9fe5abd38
- https://github.com/torvalds/linux/commit/d3bd7413e0ca40b60cf60d4003246d067cafdeda
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d3bd7413e0ca40b60cf60d4003246d067cafdeda
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1711
