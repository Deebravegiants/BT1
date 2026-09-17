# [H] netfilter: x_tables: ensure names are nul-terminated

## Summary
Severity: High
Advisory: CVE-2026-43028
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43028
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: x_tables: ensure names are nul-terminated

Reject names that lack a \0 character before feeding them
to functions that expect c-strings.

Fixes tag is the most recent commit that needs this change.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/673bbd36cba21d10a10f0932f479df7468e26fbb
- https://git.kernel.org/stable/c/73124608172890306b85f2206d8b3cac20e324f1
- https://git.kernel.org/stable/c/a958a4f90ddd7de0800b33ca9d7b886b7d40f74e
- https://git.kernel.org/stable/c/aa6cd4a8863391e0a64f62d8922cb0af732a2cf2
- https://git.kernel.org/stable/c/bcac50ea0a29d430eedc5ac87b215393b567baa9
- https://git.kernel.org/stable/c/c2d4a3abb15ca14716c6d8b9ffcbcd7c63626af4
- https://git.kernel.org/stable/c/ea01c1b219f5a11c66918abaa6f052e5a74041d6
- https://git.kernel.org/stable/c/f419bdc205894750f4d3ec042bc87a1b9cde1351
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43028.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
