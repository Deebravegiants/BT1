# [M] Users erroneously and transparently added to private messages in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-39385
Aliases: CVE-2022-39385, GHSA-gh5r-j595-qx48
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39385
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.10

## Details
Discourse is the an open source discussion platform. In some rare cases users redeeming an invitation can be added as a participant to several private message topics that they should not be added to. They are not notified of this, it happens transparently in the background. This issue has been resolved in commit `a414520742` and will be included in future releases. Users are advised to upgrade. Users are also advised to set `SiteSetting.max_invites_per_day` to 0 until the patch is installed.

## References
- https://github.com/discourse/discourse/commit/a414520742da8dc9dc976d4fb7b72dbd445813bb
- https://github.com/discourse/discourse/security/advisories/GHSA-gh5r-j595-qx48
- https://nvd.nist.gov/vuln/detail/CVE-2022-39385
