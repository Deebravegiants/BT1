# [M] CVE-2019-20795

## Summary
Severity: Medium
Advisory: CVE-2019-20795
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2019-20795
Type: osv

## Details
iproute2 before 5.1.0 has a use-after-free in get_netnsid_from_name in ip/ipnetns.c. NOTE: security relevance may be limited to certain uses of setuid that, although not a default, are sometimes a configuration option offered to end users. Even when setuid is used, other factors (such as C library configuration) may block exploitability.

## References
- https://security.gentoo.org/glsa/202008-06
- https://usn.ubuntu.com/4357-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1171452
- https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/commit/?id=9bf2c538a0eb10d66e2365a655bf6c52f5ba3d10
