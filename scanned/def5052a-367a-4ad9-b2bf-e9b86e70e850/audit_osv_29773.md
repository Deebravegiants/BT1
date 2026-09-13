# [C] nfsd: ensure that nfsd4_fattr_args.context is zeroed out

## Summary
Severity: Critical
Advisory: CVE-2024-46697
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46697
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: ensure that nfsd4_fattr_args.context is zeroed out

If nfsd4_encode_fattr4 ends up doing a "goto out" before we get to
checking for the security label, then args.context will be set to
uninitialized junk on the stack, which we'll then try to free.
Initialize it early.

## References
- https://git.kernel.org/stable/c/dd65b324174a64558a16ebbf4c3266e5701185d0
- https://git.kernel.org/stable/c/f58bab6fd4063913bd8321e99874b8239e9ba726
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46697.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
