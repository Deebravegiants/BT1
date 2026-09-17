# [H] CVE-2023-0664

## Summary
Severity: High
Advisory: CVE-2023-0664
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2023-0664
Type: osv

## Details
A flaw was found in the QEMU Guest Agent service for Windows. A local unprivileged user may be able to manipulate the QEMU Guest Agent's Windows installer via repair custom actions to elevate their privileges on the system.

## References
- https://lists.nongnu.org/archive/html/qemu-devel/2023-03/msg01445.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0664.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MURWGXDIF2WTDXV36T6HFJDBL632AO7R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SEOC7SRJWLZSXCND2ADFW6C76ZMTZLE4/
- https://nvd.nist.gov/vuln/detail/CVE-2023-0664
- https://security.netapp.com/advisory/ntap-20230517-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2167423
- https://gitlab.com/qemu-project/qemu/-/commit/07ce178a2b0768eb9e712bb5ad0cf6dc7fcf0158
- https://gitlab.com/qemu-project/qemu/-/commit/88288c2a51faa7c795f053fc8b31b1c16ff804c5
