# [H] platform/x86: dell-wmi-sysman: Fix WMI data block retrieval in sysfs callbacks

## Summary
Severity: High
Advisory: CVE-2025-38412
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38412
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: dell-wmi-sysman: Fix WMI data block retrieval in sysfs callbacks

After retrieving WMI data blocks in sysfs callbacks, check for the
validity of them before dereferencing their content.

## References
- https://git.kernel.org/stable/c/0deb3eb78ebf225cb41aa9b2b2150f46cbfd359e
- https://git.kernel.org/stable/c/5df3b870bc389a1767c72448a3ce1c576ef4deab
- https://git.kernel.org/stable/c/68e9963583d11963ceca5d276e9c44684509f759
- https://git.kernel.org/stable/c/92c2d914b5337431d885597a79a3a3d9d55e80b7
- https://git.kernel.org/stable/c/aaf847dcb4114fe8b25d4c1c790bedcb6088cb3d
- https://git.kernel.org/stable/c/eb617dd25ca176f3fee24f873f0fd60010773d67
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38412.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
