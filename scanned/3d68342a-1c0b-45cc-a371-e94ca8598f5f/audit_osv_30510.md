# [H] nvme-multipath: defer partition scanning

## Summary
Severity: High
Advisory: CVE-2024-53093
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53093
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.118, >=6.2.0 <6.6.62, >=6.7.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-multipath: defer partition scanning

We need to suppress the partition scan from occuring within the
controller's scan_work context. If a path error occurs here, the IO will
wait until a path becomes available or all paths are torn down, but that
action also occurs within scan_work, so it would deadlock. Defer the
partion scan to a different context that does not block scan_work.

## References
- https://git.kernel.org/stable/c/1f021341eef41e77a633186e9be5223de2ce5d48
- https://git.kernel.org/stable/c/4a57f42e5ed42cb8f1beb262c4f6d3e698939e4e
- https://git.kernel.org/stable/c/60de2e03f984cfbcdc12fa552f95087c35a05a98
- https://git.kernel.org/stable/c/a91b7eddf45afeeb9c5ece11dddff5de0921b00f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53093.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53093
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
