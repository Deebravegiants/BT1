# [H] CVE-2022-28893

## Summary
Severity: High
Advisory: CVE-2022-28893
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-28893
Type: osv

## Details
The SUNRPC subsystem in the Linux kernel through 5.17.2 can call xs_xprt_free before ensuring that sockets are in the intended state.

## References
- https://security.netapp.com/advisory/ntap-20220526-0002/
- https://www.debian.org/security/2022/dsa-5161
- http://www.openwall.com/lists/oss-security/2022/04/11/3
- http://www.openwall.com/lists/oss-security/2022/04/11/4
- http://www.openwall.com/lists/oss-security/2022/04/11/5
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1a3b1bba7c7a5eb8a11513cf88427cb9d77bc60a
