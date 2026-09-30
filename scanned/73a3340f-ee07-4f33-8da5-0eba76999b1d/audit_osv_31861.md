# [M] ftrace: Avoid potential division by zero in function_stat_show()

## Summary
Severity: Medium
Advisory: CVE-2025-21898
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21898
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.291, >=5.5.0 <5.15.179, >=5.11.0 <6.1.130, >=5.16.0 <6.6.81, >=6.2.0 <6.12.18, >=6.7.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Avoid potential division by zero in function_stat_show()

Check whether denominator expression x * (x - 1) * 1000 mod {2^32, 2^64}
produce zero and skip stddev computation in that case.

For now don't care about rec->counter * rec->counter overflow because
rec->time * rec->time overflow will likely happen earlier.

## References
- https://git.kernel.org/stable/c/3d738b53ed6cddb68e68c9874520a4bf846163b5
- https://git.kernel.org/stable/c/5b3d32f607f0478b414b16516cf27f9170cf66c8
- https://git.kernel.org/stable/c/746cc474a95473591853927b3a9792a2d671155b
- https://git.kernel.org/stable/c/992775227843c9376773784b8b362add44592ad7
- https://git.kernel.org/stable/c/9cdac46fa7e854e587eb5f393fe491b6d7a9bdf6
- https://git.kernel.org/stable/c/a1a7eb89ca0b89dc1c326eeee2596f263291aca3
- https://git.kernel.org/stable/c/ca381f60a3bb7cfaa618d73ca411610bd7fc3149
- https://git.kernel.org/stable/c/f58a3f8e284d0bdf94164a8e61cd4e70d337a1a3
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21898.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21898
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
