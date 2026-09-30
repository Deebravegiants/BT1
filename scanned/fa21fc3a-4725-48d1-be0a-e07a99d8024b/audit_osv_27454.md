# [M] rubygems.org MFA Bypass through password reset function could allow account takeover

## Summary
Severity: Medium
Advisory: CVE-2024-21654
Aliases: GHSA-4v23-vj8h-7jp2
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2024-21654
Type: osv

## Details
Rubygems.org is the Ruby community's gem hosting service. Rubygems.org users with MFA enabled would normally be protected from account takeover in the case of email account takeover. However, a workaround on the forgotten password form allows an attacker to bypass the MFA requirement and takeover the account. This vulnerability has been patched in commit 0b3272a.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21654.json
- https://github.com/rubygems/rubygems.org/security/advisories/GHSA-4v23-vj8h-7jp2
- https://nvd.nist.gov/vuln/detail/CVE-2024-21654
- https://github.com/rubygems/rubygems.org/commit/0b3272ac17b45748ee0d1867c49867c7deb26565
