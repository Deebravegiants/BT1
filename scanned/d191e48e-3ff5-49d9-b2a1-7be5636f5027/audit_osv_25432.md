# [H] The King's Temple Church website Leaked Stripe API Key in Public Code Repository

## Summary
Severity: High
Advisory: CVE-2023-36817
Aliases: GHSA-x3m6-5hmf-5x3w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-03
Source: https://osv.dev/vulnerability/CVE-2023-36817
Type: osv

## Details
`tktchurch/website` contains the codebase for The King's Temple Church website. In version 0.1.0, a Stripe API key was found in the public code repository of the church's project. This sensitive information was unintentionally committed and subsequently exposed in the codebase. If an unauthorized party gains access to this key, they could potentially carry out transactions on behalf of the organization, leading to financial losses. Additionally, they could access sensitive customer information, leading to privacy violations and potential legal implications. The affected component is the codebase of our project, specifically the file(s) where the Stripe API key is embedded. The key should have been stored securely, and not committed to the codebase. The maintainers plan to revoke the leaked Stripe API key immediately, generate a new one, and not commit the key to the codebase.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36817.json
- https://github.com/tktchurch/website/security/advisories/GHSA-x3m6-5hmf-5x3w
- https://nvd.nist.gov/vuln/detail/CVE-2023-36817
