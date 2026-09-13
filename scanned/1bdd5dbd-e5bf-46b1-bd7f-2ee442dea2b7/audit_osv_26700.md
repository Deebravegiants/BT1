# [H] scsi: qla2xxx: Fix deletion race condition

## Summary
Severity: High
Advisory: CVE-2023-53615
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53615
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.258, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix deletion race condition

System crash when using debug kernel due to link list corruption. The cause
of the link list corruption is due to session deletion was allowed to queue
up twice.  Here's the internal trace that show the same port was allowed to
double queue for deletion on different cpu.

20808683956 015 qla2xxx [0000:13:00.1]-e801:4: Scheduling sess ffff93ebf9306800 for deletion 50:06:0e:80:12:48:ff:50 fc4_type 1
20808683957 027 qla2xxx [0000:13:00.1]-e801:4: Scheduling sess ffff93ebf9306800 for deletion 50:06:0e:80:12:48:ff:50 fc4_type 1

Move the clearing/setting of deleted flag lock.

## References
- https://git.kernel.org/stable/c/4d7da12483e98c451a51bd294a3d3494f0aee5eb
- https://git.kernel.org/stable/c/6dfe4344c168c6ca20fe7640649aacfcefcccb26
- https://git.kernel.org/stable/c/a4628a5b98e4c6d905e1f7638242612d7db7d9c2
- https://git.kernel.org/stable/c/b05017cb4ff75eea783583f3d400059507510ab1
- https://git.kernel.org/stable/c/cd06c45b326e44f0d21dc1b3fa23e71f46847e28
- https://git.kernel.org/stable/c/f1ea164be545629bf442c22f508ad9e7b94ac100
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53615.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53615
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
