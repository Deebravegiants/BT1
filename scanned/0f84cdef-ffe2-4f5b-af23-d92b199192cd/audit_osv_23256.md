# [M] Discourse password reset link can lead to in account takeover if user changes to a new email

## Summary
Severity: Medium
Advisory: CVE-2022-46177
Aliases: BIT-discourse-2022-46177, GHSA-5www-jxvf-vrc3
CVSS: 5.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N)
Published: 2023-01-05
Source: https://osv.dev/vulnerability/CVE-2022-46177
Type: osv

## Details
Discourse is an option source discussion platform. Prior to version 2.8.14 on the `stable` branch and version 3.0.0.beta16 on the `beta` and `tests-passed` branches, when a user requests for a password reset link email, then changes their primary email, the old reset email is still valid. When the old reset email is used to reset the password, the Discourse account's primary email would be re-linked to the old email. If the old email address is compromised or has transferred ownership, this leads to an account takeover. This is however mitigated by the SiteSetting `email_token_valid_hours` which is currently 48 hours. Users should upgrade to versions 2.8.14 or 3.0.0.beta15 to receive a patch. As a workaround, lower `email_token_valid_hours ` as needed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46177.json
- https://github.com/discourse/discourse/security/advisories/GHSA-5www-jxvf-vrc3
- https://nvd.nist.gov/vuln/detail/CVE-2022-46177
- https://github.com/discourse/discourse/commit/4bf306f0e3bf54a9ef9c5886bf1cfb85c20da570
- https://github.com/discourse/discourse/commit/83944213b2b2454af80d0407f60d67641b1f0b38
