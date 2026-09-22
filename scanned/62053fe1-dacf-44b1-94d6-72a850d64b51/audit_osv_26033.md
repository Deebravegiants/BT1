# [M] CVE-2023-49721

## Summary
Severity: Medium
Advisory: CVE-2023-49721
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-49721
Type: osv

## Details
An insecure default to allow UEFI Shell in EDK2 was left enabled in LXD. This allows an OS-resident attacker to bypass Secure Boot.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49721.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49721
- https://bugs.launchpad.net/ubuntu/+source/edk2/+bug/2040137
- https://bugs.launchpad.net/ubuntu/+source/lxd/+bug/2040139
- https://nvd.nist.gov/vuln/detail/CVE-2023-48733
- https://www.openwall.com/lists/oss-security/2024/02/14/4
