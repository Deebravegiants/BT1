# [H] rust_binder: avoid reading the written value in offsets array

## Summary
Severity: High
Advisory: CVE-2026-43433
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43433
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

rust_binder: avoid reading the written value in offsets array

When sending a transaction, its offsets array is first copied into the
target proc's vma, and then the values are read back from there. This is
normally fine because the vma is a read-only mapping, so the target
process cannot change the value under us.

However, if the target process somehow gains the ability to write to its
own vma, it could change the offset before it's read back, causing the
kernel to misinterpret what the sender meant. If the sender happens to
send a payload with a specific shape, this could in the worst case lead
to the receiver being able to privilege escalate into the sender.

The intent is that gaining the ability to change the read-only vma of
your own process should not be exploitable, so remove this TOCTOU read
even though it's unexploitable without another Binder bug.

## References
- https://git.kernel.org/stable/c/3672141c93b7a0c0132bf5d5021a4b7f1d663aaa
- https://git.kernel.org/stable/c/4cb9e13fec0de7c942f5f927469beb8e48ddd20f
- https://git.kernel.org/stable/c/e19afb53f7723b3bd22224f2b0c7dcfa70bb973f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43433
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
