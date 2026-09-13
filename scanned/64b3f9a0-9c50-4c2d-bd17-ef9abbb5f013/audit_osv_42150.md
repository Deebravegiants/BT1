# [H] smb/client: Fix error code in smb2_aead_req_alloc()

## Summary
Severity: High
Advisory: CVE-2026-64598
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64598
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: Fix error code in smb2_aead_req_alloc()

The "*num_sgs" variable is a u32 so "ERR_PTR(*num_sgs)" doesn't work.
We would have to do something similar to the previous line where it's
cast to int and then long.  However, it's simpler to store the return in
an int ret variable.

This bug would eventually result in a crash when dereference the invalid
error pointer.

## References
- https://git.kernel.org/stable/c/61f28012e5650c619223decdb7970e0d3162e949
- https://git.kernel.org/stable/c/a187883cc1dc784a4d32537f5d316f1b7b9ad76f
- https://git.kernel.org/stable/c/a1cc432cb0b0a1f74f98a0db3b94ca880c7947ac
- https://git.kernel.org/stable/c/aa37f5fef78dd11cbf983269da2031e12625c56d
- https://git.kernel.org/stable/c/cad756733dc3985188983f3e2eb77e2927209099
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
