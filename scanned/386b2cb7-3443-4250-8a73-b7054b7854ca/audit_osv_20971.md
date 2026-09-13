# [M] CVE-2021-39210

## Summary
Severity: Medium
Advisory: CVE-2021-39210
Aliases: GHSA-hwxq-4c5f-m4v2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CVE-2021-39210
Type: osv

## Details
GLPI is a free Asset and IT management software package. In versions prior to 9.5.6, the cookie used to store the autologin cookie (when a user uses the "remember me" feature) is accessible by scripts. A malicious plugin that could steal this cookie would be able to use it to autologin. This issue is fixed in version 9.5.6. As a workaround, one may avoid using the "remember me" feature.

## References
- https://github.com/glpi-project/glpi/releases/tag/9.5.6
- https://github.com/glpi-project/glpi/security/advisories/GHSA-hwxq-4c5f-m4v2
- https://huntr.dev/bounties/b2e99a41-b904-419f-a274-ae383e4925f2/
