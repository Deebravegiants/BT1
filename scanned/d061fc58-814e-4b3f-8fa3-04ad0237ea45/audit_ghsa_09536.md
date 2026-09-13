# [H] ZITADEL has LDAP Filter Injection in Login Flow

## Summary
Severity: High
Advisory: GHSA-rxvx-hhpj-q6px
CVE: CVE-2026-44671
CWE: CWE-90
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-rxvx-hhpj-q6px
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0 <4.15.0
- Go: `github.com/zitadel/zitadel` — affected >=2.71.11
- Go: `github.com/zitadel/zitadel` — affected >=3.1.0 <3.4.10

## Details
## Summary

A vulnerability was discovered in Zitadel's LDAP identity provider implementation, which fails to properly escape user-provided usernames before incorporating them into LDAP search filters. This allows unauthenticated attackers to perform LDAP Filter Injection during the login process.

## Impact

While this vulnerability does not allow for a full authentication bypass, an attacker can use LDAP metacharacters (such as `*`, `(`, `)`) to perform blind LDAP injection. By observing the different failure (or success) responses, an attacker can systematically enumerate valid usernames and extract sensitive attribute data from the connected LDAP directory.

Note that an authentication bypass is not possible.

## Affected Versions

Systems integrating LDAP as IdPs and running one of the following versions are affected:

- **4.x**: `4.0.0` through `4.14.0` (including RC versions)
- **3.x**: `3.1.0` through `3.4.9`
- **2.x**: `2.71.11` through `2.71.19`

## Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by requiring the correct permission in case the verification flag is provided and only allows self-management of the email address, resp. phone number itself.

- **4.x**: Upgrade to >=[4.15.0](https://github.com/zitadel/zitadel/releases/tag/v4.15.0)
- **3.x**: Update to >=[3.4.10](https://github.com/zitadel/zitadel/releases/tag/v3.4.10)
- **2.x**: Update to >=[3.4.10](https://github.com/zitadel/zitadel/releases/tag/v3.4.10)

## Workarounds

The recommended solution is to upgrade to a patched version. If an immediate upgrade is not possible, developers should ensure their project's LDAP directory has strict access controls to limit the scope of information disclosure.

## Questions

If there are any questions or comments about this advisory, please send an email to [security@zitadel.com](mailto:security@zitadel.com)

## Credits

This vulnerability was identified and reported by **ProScan AppSec** ([https://proscan.one/](https://proscan.one)).

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-rxvx-hhpj-q6px
- https://nvd.nist.gov/vuln/detail/CVE-2026-44671
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.10
- https://github.com/zitadel/zitadel/releases/tag/v4.15.0
