# [H] CVE-2022-0204

## Summary
Severity: High
Advisory: CVE-2022-0204
Aliases: GHSA-479m-xcq5-9g2q
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-09
Source: https://osv.dev/vulnerability/CVE-2022-0204
Type: osv

## Details
A heap overflow vulnerability was found in bluez in versions prior to 5.63. An attacker with local network access could pass specially crafted files causing an application to halt or crash, leading to a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0204.json
- https://github.com/bluez/bluez/security/advisories/GHSA-479m-xcq5-9g2q
- https://nvd.nist.gov/vuln/detail/CVE-2022-0204
- https://security.gentoo.org/glsa/202209-16
- https://bugzilla.redhat.com/show_bug.cgi?id=2039807
- https://github.com/bluez/bluez/commit/591c546c536b42bef696d027f64aa22434f8c3f0
- https://lists.debian.org/debian-lts-announce/2022/10/msg00026.html
