# [H] f2fs: fix dereference of stale list iterator after loop body

## Summary
Severity: High
Advisory: CVE-2022-49425
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49425
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix dereference of stale list iterator after loop body

The list iterator variable will be a bogus pointer if no break was hit.
Dereferencing it (cur->page in this case) could load an out-of-bounds/undefined
value making it unsafe to use that in the comparision to determine if the
specific element was found.

Since 'cur->page' *can* be out-ouf-bounds it cannot be guaranteed that
by chance (or intention of an attacker) it matches the value of 'page'
even though the correct element was not found.

This is fixed by using a separate list iterator variable for the loop
and only setting the original variable if a suitable element was found.
Then determing if the element was found is simply checking if the
variable is set.

## References
- https://git.kernel.org/stable/c/2aaf51dd39afb6d01d13f1e6fe20b684733b37d5
- https://git.kernel.org/stable/c/385edd3ce5b4b1e9d31f474a5e35a39779ec1110
- https://git.kernel.org/stable/c/45b2b7d7108ae1e25a5036cab04ab9273e792332
- https://git.kernel.org/stable/c/51d584704d18e60fa473823654f35611c777b291
- https://git.kernel.org/stable/c/5e47a7add3dda7f236548c5ec3017776dc2a729f
- https://git.kernel.org/stable/c/b26e1c777890e4b938136deb8ec07a29f33862e4
- https://git.kernel.org/stable/c/ed7efc472c00986dcd6903ab6ed165c7fa167674
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49425.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
