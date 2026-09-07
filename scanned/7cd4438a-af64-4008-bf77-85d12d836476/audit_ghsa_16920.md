# [M] OpenID Connect Authentication (oidc) Typo3 extension Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-hhf8-f5w9-g6vh
CVE: CVE-2024-30173
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N/E:F/RL:O/RC:C (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-hhf8-f5w9-g6vh
Type: github-advisory

## Affected
- Packagist: `causal/oidc` — affected >=0 <2.1.0

## Details
The authentication service of the extension does not verify the OpenID Connect authentication state from the user lookup chain. Instead, the authentication service authenticates every valid frontend user from the user lookup chain, where the  frontend user field “tx_oidc” is not empty.

In scenarios, where either ext:felogin is active or where `$GLOBALS['TYPO3_CONF_VARS'][‘FE’][‘checkFeUserPid’]` is disabled, an attacker can login to OpenID Connect frontend user accounts by providing a valid username and any password.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/causal/oidc/CVE-2024-30173.yaml
- https://github.com/xperseguers/t3ext-oidc
- https://typo3.org/security/advisory/typo3-ext-sa-2024-002
