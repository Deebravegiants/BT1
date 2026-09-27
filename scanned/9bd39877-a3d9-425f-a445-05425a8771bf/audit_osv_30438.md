# [M] Missing validation allows spoofed profiles in Misskey

## Summary
Severity: Medium
Advisory: CVE-2024-52590
Aliases: GHSA-7vgr-p3vc-p4h2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:L/SI:N/SA:L)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-52590
Type: osv

## Details
Misskey is an open source, federated social media platform. In affected versions missing validation in `ApRequestService.signedGet` allows an attacker to create fake user profiles that appear to be from a different instance than the one where they actually exist. These profiles can be used to impersonate existing users from the target instance. Vulnerable Misskey instances will accept spoofed users as valid, allowing an attacker to impersonate users on another instance. Attackers have full control of the spoofed user and can post, renote, or otherwise interact like a real account. This issue has been addressed in version 2024.11.0-alpha.3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52590.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-7vgr-p3vc-p4h2
- https://nvd.nist.gov/vuln/detail/CVE-2024-52590
