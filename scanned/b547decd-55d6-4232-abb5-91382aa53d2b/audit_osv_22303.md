# [M] Improper access control in humhub

## Summary
Severity: Medium
Advisory: CVE-2022-24865
Aliases: GHSA-2h35-f226-3f57
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-20
Source: https://osv.dev/vulnerability/CVE-2022-24865
Type: osv

## Details
HumHub is an Open Source Enterprise Social Network. In affected versions users who are forced to change their password by an administrator may retrieve other users' data. This issue has been resolved by commit `eb83de20`. It is recommended that the HumHub is upgraded to 1.11.0, 1.10.4 or 1.9.4. There are no known workarounds for this issue.

## References
- https://huntr.dev/bounties/89d996a2-de30-4261-8e3f-98e54cb25f76/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24865.json
- https://github.com/humhub/humhub/security/advisories/GHSA-2h35-f226-3f57
- https://nvd.nist.gov/vuln/detail/CVE-2022-24865
- https://github.com/humhub/humhub/commit/eb83de20aaecc559ab77a44a6179646a99607e33
