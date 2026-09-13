# [H] media: venus: hfi_parser: refactor hfi packet parsing logic

## Summary
Severity: High
Advisory: CVE-2025-23156
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23156
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: hfi_parser: refactor hfi packet parsing logic

words_count denotes the number of words in total payload, while data
points to payload of various property within it. When words_count
reaches last word, data can access memory beyond the total payload. This
can lead to OOB access. With this patch, the utility api for handling
individual properties now returns the size of data consumed. Accordingly
remaining bytes are calculated before parsing the payload, thereby
eliminates the OOB access possibilities.

## References
- https://git.kernel.org/stable/c/05b07e52a0d08239147ba3460045855f4fb398de
- https://git.kernel.org/stable/c/0beabe9b49190a02321b02792b29fc0f0e28b51f
- https://git.kernel.org/stable/c/0f9a4bab7d83738963365372e4745854938eab2d
- https://git.kernel.org/stable/c/6d278c5548d840c4d85d445347b2a5c31b2ab3a0
- https://git.kernel.org/stable/c/9edaaa8e3e15aab1ca413ab50556de1975bcb329
- https://git.kernel.org/stable/c/a736c72d476d1c7ca7be5018f2614ee61168ad01
- https://git.kernel.org/stable/c/bb3fd8b7906a12dc2b61389abb742bf6542d97fb
- https://git.kernel.org/stable/c/f195e94c7af921d99abd79f57026a218d191d2c7
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23156.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
