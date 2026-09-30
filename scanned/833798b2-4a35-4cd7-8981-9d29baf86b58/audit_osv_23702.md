# [C] NFSD: Fix potential use-after-free in nfsd_file_put()

## Summary
Severity: Critical
Advisory: CVE-2022-49362
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49362
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix potential use-after-free in nfsd_file_put()

nfsd_file_put_noref() can free @nf, so don't dereference @nf
immediately upon return from nfsd_file_put_noref().

## References
- https://git.kernel.org/stable/c/261eabe19cb28e4a8587a4442d257b543d7c2d57
- https://git.kernel.org/stable/c/333dcc94ebf53f79f3dc0e7a7c16700bc7ff7e57
- https://git.kernel.org/stable/c/ada1757b259f353cade47037ee0a0249b4cddad3
- https://git.kernel.org/stable/c/b6c71c66b0ad8f2b59d9bc08c7a5079b110bec01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49362.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49362
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
