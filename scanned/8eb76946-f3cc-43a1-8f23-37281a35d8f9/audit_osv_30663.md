# [C] openwrt/asu allows build artifact poisoning via truncated SHA-256 hash and command injection

## Summary
Severity: Critical
Advisory: CVE-2024-54143
Aliases: GHSA-r3gq-96h6-3v7q
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-06
Source: https://osv.dev/vulnerability/CVE-2024-54143
Type: osv

## Details
openwrt/asu is an image on demand server for OpenWrt based distributions. The request hashing mechanism truncates SHA-256 hashes to only 12 characters. This significantly reduces entropy, making it feasible for an attacker to generate collisions. By exploiting this, a previously built malicious image can be served in place of a legitimate one, allowing the attacker to "poison" the artifact cache and deliver compromised images to unsuspecting users. This can be combined with other attacks, such as a command injection in Imagebuilder that allows malicious users to inject arbitrary commands into the build process, resulting in the production of malicious firmware images signed with the legitimate build key. This has been patched with 920c8a1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54143.json
- https://github.com/openwrt/asu/security/advisories/GHSA-r3gq-96h6-3v7q
- https://nvd.nist.gov/vuln/detail/CVE-2024-54143
- https://github.com/openwrt/asu/commit/920c8a13d97b4d4095f0d939cf0aaae777e0f87e
