# [C] nfsd: fix potential UAF in nfsd4_cb_getattr_release

## Summary
Severity: Critical
Advisory: CVE-2024-46696
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46696
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix potential UAF in nfsd4_cb_getattr_release

Once we drop the delegation reference, the fields embedded in it are no
longer safe to access. Do that last.

## References
- https://git.kernel.org/stable/c/1116e0e372eb16dd907ec571ce5d4af325c55c10
- https://git.kernel.org/stable/c/e0b66698a5ae41078f7490e8b3527013f5fccd6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46696.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
