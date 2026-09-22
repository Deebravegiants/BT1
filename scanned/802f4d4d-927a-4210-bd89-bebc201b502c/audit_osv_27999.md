# [H] ksmbd: fix potencial out-of-bounds when buffer offset is invalid

## Summary
Severity: High
Advisory: CVE-2024-26952
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26952
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.181, >=5.16.0 <6.1.119, >=6.2.0 <6.6.32, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix potencial out-of-bounds when buffer offset is invalid

I found potencial out-of-bounds when buffer offset fields of a few requests
is invalid. This patch set the minimum value of buffer offset field to
->Buffer offset to validate buffer length.

## References
- https://git.kernel.org/stable/c/0c5541b4c980626fa3cab16ba1a451757778bbb5
- https://git.kernel.org/stable/c/2dcda336b6e80b72d58d30d40f2fad9724e5fe63
- https://git.kernel.org/stable/c/39bdc4197acf2ed13269167ccf093ee28cfa2a4e
- https://git.kernel.org/stable/c/480469f145e5abf83361e608734e421b7d99693d
- https://git.kernel.org/stable/c/ad6480c9a5d884e2704adc51d69895d93339176c
- https://git.kernel.org/stable/c/c6cd2e8d2d9aa7ee35b1fa6a668e32a22a9753da
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26952.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
