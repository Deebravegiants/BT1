# [H] ASoC: topology: Fix references to freed memory

## Summary
Severity: High
Advisory: CVE-2024-41069
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41069
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: topology: Fix references to freed memory

Most users after parsing a topology file, release memory used by it, so
having pointer references directly into topology file contents is wrong.
Use devm_kmemdup(), to allocate memory as needed.

## References
- https://git.kernel.org/stable/c/97ab304ecd95c0b1703ff8c8c3956dc6e2afe8e1
- https://git.kernel.org/stable/c/ab5a6208b4d6872b1c6ecea1867940fc668cc76d
- https://git.kernel.org/stable/c/b188d7f3dfab10e332e3c1066e18857964a520d2
- https://git.kernel.org/stable/c/ccae5c6a1fab9494c86b7856faf05e296c617702
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
