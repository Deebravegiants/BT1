# [M] Concrete CMS vulnerable to Cleartext Transmission of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-q3hq-hm5h-qrx3
CVE: CVE-2022-43691
CWE: CWE-319
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-q3hq-hm5h-qrx3
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.10
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.1.3

## Details
Concrete CMS (formerly concrete5) below 8.5.10 and between 9.0.0 and 9.1.2 inadvertently disclose server-side sensitive information (secrets in environment variables and server information) when Debug Mode is left on in production.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43691
- https://documentation.concretecms.org/developers/introduction/version-history/8510-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/913-release-notes
- https://github.com/concretecms/concretecms
- https://github.com/concretecms/concretecms/releases/8.5.10
- https://github.com/concretecms/concretecms/releases/9.1.3
- https://www.concretecms.org/about/project-news/security/concrete-cms-security-advisory-2022-10-31
