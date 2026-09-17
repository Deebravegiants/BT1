# [H] Revert "NFSD: Remove the cap on number of operations per NFSv4 COMPOUND"

## Summary
Severity: High
Advisory: CVE-2025-40210
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-40210
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "NFSD: Remove the cap on number of operations per NFSv4 COMPOUND"

I've found that pynfs COMP6 now leaves the connection or lease in a
strange state, which causes CLOSE9 to hang indefinitely. I've dug
into it a little, but I haven't been able to root-cause it yet.
However, I bisected to commit 48aab1606fa8 ("NFSD: Remove the cap on
number of operations per NFSv4 COMPOUND").

Tianshuo Han also reports a potential vulnerability when decoding
an NFSv4 COMPOUND. An attacker can place an arbitrarily large op
count in the COMPOUND header, which results in:

[   51.410584] nfsd: vmalloc error: size 1209533382144, exceeds total
pages, mode:0xdc0(GFP_KERNEL|__GFP_ZERO),
nodemask=(null),cpuset=/,mems_allowed=0

when NFSD attempts to allocate the COMPOUND op array.

Let's restore the operation-per-COMPOUND limit, but increased to 200
for now.

## References
- https://git.kernel.org/stable/c/3e7f011c255582d7c914133785bbba1990441713
- https://git.kernel.org/stable/c/b3ee7ce432289deac87b9d14e01f2fe6958f7f0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40210.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
