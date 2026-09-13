# [H] media: aspeed: Fix memory overwrite if timing is 1600x900

## Summary
Severity: High
Advisory: CVE-2023-52916
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2023-52916
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.1.120

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: aspeed: Fix memory overwrite if timing is 1600x900

When capturing 1600x900, system could crash when system memory usage is
tight.

The way to reproduce this issue:
1. Use 1600x900 to display on host
2. Mount ISO through 'Virtual media' on OpenBMC's web
3. Run script as below on host to do sha continuously
  #!/bin/bash
  while [ [1] ];
  do
	find /media -type f -printf '"%h/%f"\n' | xargs sha256sum
  done
4. Open KVM on OpenBMC's web

The size of macro block captured is 8x8. Therefore, we should make sure
the height of src-buf is 8 aligned to fix this issue.

## References
- https://git.kernel.org/stable/c/4c823e4027dd1d6e88c31028dec13dd19bc7b02d
- https://git.kernel.org/stable/c/c281355068bc258fd619c5aefd978595bede7bfe
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52916.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
