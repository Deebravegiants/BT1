# [H] crypto: s390/aes - Fix buffer overread in CTR mode

## Summary
Severity: High
Advisory: CVE-2023-52669
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52669
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: s390/aes - Fix buffer overread in CTR mode

When processing the last block, the s390 ctr code will always read
a whole block, even if there isn't a whole block of data left.  Fix
this by using the actual length left and copy it into a buffer first
for processing.

## References
- https://git.kernel.org/stable/c/a7f580cdb42ec3d53bbb7c4e4335a98423703285
- https://git.kernel.org/stable/c/cd51e26a3b89706beec64f2d8296cfb1c34e0c79
- https://git.kernel.org/stable/c/d07f951903fa9922c375b8ab1ce81b18a0034e3b
- https://git.kernel.org/stable/c/d68ac38895e84446848b7647ab9458d54cacba3e
- https://git.kernel.org/stable/c/dbc9a791a70ea47be9f2acf251700fe254a2ab23
- https://git.kernel.org/stable/c/e78f1a43e72daf77705ad5b9946de66fc708b874
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52669.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
