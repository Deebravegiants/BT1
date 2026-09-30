# [C] smb: client: fix possible double free in smb2_set_ea()

## Summary
Severity: Critical
Advisory: CVE-2024-50152
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50152
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix possible double free in smb2_set_ea()

Clang static checker(scan-build) warning：
fs/smb/client/smb2ops.c:1304:2: Attempt to free released memory.
 1304 |         kfree(ea);
      |         ^~~~~~~~~

There is a double free in such case:
'ea is initialized to NULL' -> 'first successful memory allocation for
ea' -> 'something failed, goto sea_exit' -> 'first memory release for ea'
-> 'goto replay_again' -> 'second goto sea_exit before allocate memory
for ea' -> 'second memory release for ea resulted in double free'.

Re-initialie 'ea' to NULL near to the replay_again label, it can fix this
double free problem.

## References
- https://git.kernel.org/stable/c/19ebc1e6cab334a8193398d4152deb76019b5d34
- https://git.kernel.org/stable/c/b1813c220b76f60b1727984794377c4aa849d4c1
- https://git.kernel.org/stable/c/c9f758ecf2562dfdd4adf12c22921b5de8366123
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50152.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50152
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
