# [M] CVE-2023-48733

## Summary
Severity: Medium
Advisory: CVE-2023-48733
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-48733
Type: osv

## Details
An insecure default to allow UEFI Shell in EDK2 was left enabled in Ubuntu's EDK2. This allows an OS-resident attacker to bypass Secure Boot.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48733.json
- https://bugs.launchpad.net/ubuntu/+source/edk2/+bug/2040137
- https://bugs.launchpad.net/ubuntu/+source/lxd/+bug/2040139
- https://nvd.nist.gov/vuln/detail/CVE-2023-48733
- https://www.openwall.com/lists/oss-security/2024/02/14/4
