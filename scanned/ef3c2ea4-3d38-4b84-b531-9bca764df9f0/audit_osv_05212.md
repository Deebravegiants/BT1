# [C] BIT-gitlab-2022-1680

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-1680
Aliases: CVE-2022-1680
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1680
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.0.0 <15.0.1

## Details
An account takeover issue has been discovered in GitLab EE affecting all versions starting from 11.10 before 14.9.5, all versions starting from 14.10 before 14.10.4, all versions starting from 15.0 before 15.0.1. When group SAML SSO is configured, the SCIM feature (available only on Premium+ subscriptions) may allow any owner of a Premium group to invite arbitrary users through their username and email, then change those users' email addresses via SCIM to an attacker controlled email address and thus - in the absence of 2FA - take over those accounts. It is also possible for the attacker to change the display name and username of the targeted account.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1680.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/363058
- https://nvd.nist.gov/vuln/detail/CVE-2022-1680
