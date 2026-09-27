# [H] scsi: qla2xxx: Fix for possible memory corruption

## Summary
Severity: High
Advisory: CVE-2024-42288
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42288
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix for possible memory corruption

Init Control Block is dereferenced incorrectly.  Correctly dereference ICB

## References
- https://git.kernel.org/stable/c/2a15b59a2c5afac89696e44acf5bbfc0599c6c5e
- https://git.kernel.org/stable/c/571d7f2a08836698c2fb0d792236424575b9829b
- https://git.kernel.org/stable/c/8192c533e89d9fb69b2490398939236b78cda79b
- https://git.kernel.org/stable/c/87db8d7b7520e99de71791260989f06f9c94953d
- https://git.kernel.org/stable/c/b0302ffc74123b6a99d7d1896fcd9b2e4072d9ce
- https://git.kernel.org/stable/c/c03d740152f78e86945a75b2ad541bf972fab92a
- https://git.kernel.org/stable/c/dae67169cb35a37ecccf60cfcd6bf93a1f4f5efb
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42288.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
