# [C] NFSD: prevent underflow in nfssvc_decode_writeargs()

## Summary
Severity: Critical
Advisory: CVE-2022-49280
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49280
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: prevent underflow in nfssvc_decode_writeargs()

Smatch complains:

	fs/nfsd/nfsxdr.c:341 nfssvc_decode_writeargs()
	warn: no lower bound on 'args->len'

Change the type to unsigned to prevent this issue.

## References
- https://git.kernel.org/stable/c/184416d4b98509fb4c3d8fc3d6dc1437896cc159
- https://git.kernel.org/stable/c/2764af8ce0bf03cc43ee4a11897cab96bde6caae
- https://git.kernel.org/stable/c/413d8fefafe531a9442bb623e3fe292a38f88d65
- https://git.kernel.org/stable/c/614a61e1592051cc42d3c38f899c9f7bdaad8a1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49280.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
