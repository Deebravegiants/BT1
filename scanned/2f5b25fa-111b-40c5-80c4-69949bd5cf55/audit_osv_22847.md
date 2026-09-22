# [M] Metabase SSO users able to circumvent IdP login by doing password reset

## Summary
Severity: Medium
Advisory: CVE-2022-39360
Aliases: GHSA-gw4g-ww2m-v7vc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39360
Type: osv

## Details
Metabase is data visualization software. Prior to versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9 single sign on (SSO) users were able to do password resets on Metabase, which could allow a user access without going through the SSO IdP. This issue is patched in versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9. Metabase now blocks password reset for all users who use SSO for their Metabase login.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39360.json
- https://github.com/metabase/metabase/security/advisories/GHSA-gw4g-ww2m-v7vc
- https://nvd.nist.gov/vuln/detail/CVE-2022-39360
- https://github.com/metabase/metabase/commit/edadf7303c3b068609f57ca073e67885d5c98730
