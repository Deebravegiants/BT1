# [H] TYPO3 Security Misconfiguration for Backend User Accounts

## Summary
Severity: High
Advisory: GHSA-c5mj-39cf-3pp5
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-c5mj-39cf-3pp5
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
When using the TYPO3 backend in order to create new backend user accounts, database records containing insecure or empty credentials might be persisted. When the type of user account is changed - which might be entity type or the admin flag for backend users - the backend form is reloaded in order to reflect changed configuration possibilities. However, this leads to persisting the current state as well, which can result into some of the following:

- account contains empty login credentials (username and/or password)
- account is incomplete and contains weak credentials (username and/or password)

Albeit the functionality provided by the TYPO3 core cannot be used either with empty usernames or empty passwords, it still can be a severe vulnerability to custom authentication service implementations.

This weakness cannot be directly exploited and requires interaction on purpose by some backend user having according privileges.

## References
- https://github.com/TYPO3/typo3/commit/b3608d14e1915030cde272000a247cb6d5f982b8
- https://github.com/TYPO3/typo3/commit/e4d0cff40a4f8f597e52c20fff529e206bb62703
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-002
