# [H] User session not correctly destroyed on logout

## Summary
Severity: High
Advisory: CVE-2023-32318
Aliases: GHSA-q8c4-chpj-6v38
CVSS: 7.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32318
Type: osv

## Details
Nextcloud server provides a home for data. A regression in the session handling between Nextcloud Server and the Nextcloud Text app prevented a correct destruction of the session on logout if cookies were not cleared manually. After successfully authenticating with any other account the previous session would be continued and the attacker would be authenticated as the previously logged in user. It is recommended that the Nextcloud Server is upgraded to 25.0.6 or 26.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32318.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-q8c4-chpj-6v38
- https://nvd.nist.gov/vuln/detail/CVE-2023-32318
- https://github.com/nextcloud/text/pull/3946
