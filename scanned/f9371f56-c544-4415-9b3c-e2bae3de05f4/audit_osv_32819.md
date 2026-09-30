# [H] orangefs: Do not truncate file size

## Summary
Severity: High
Advisory: CVE-2025-38065
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38065
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

orangefs: Do not truncate file size

'len' is used to store the result of i_size_read(), so making 'len'
a size_t results in truncation to 4GiB on 32-bit systems.

## References
- https://git.kernel.org/stable/c/062e8093592fb866b8e016641a8b27feb6ac509d
- https://git.kernel.org/stable/c/121f0335d91e46369bf55b5da4167d82b099a166
- https://git.kernel.org/stable/c/15602508ad2f923e228b9521960b4addcd27d9c4
- https://git.kernel.org/stable/c/2323b806221e6268a4e17711bc72e2fc87c191a3
- https://git.kernel.org/stable/c/341e3a5984cf5761f3dab16029d7e9fb1641d5ff
- https://git.kernel.org/stable/c/5111227d7f1f57f6804666b3abf780a23f44fc1d
- https://git.kernel.org/stable/c/cd918ec24168fe08c6aafc077dd3b6d88364c5cf
- https://git.kernel.org/stable/c/ceaf195ed285b77791e29016ee6344b3ded609b3
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38065.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
