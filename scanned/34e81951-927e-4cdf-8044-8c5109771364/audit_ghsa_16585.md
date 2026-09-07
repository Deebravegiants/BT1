# [M] Shopware Non-Persistent XSS in the Frontend

## Summary
Severity: Medium
Advisory: GHSA-jqr7-5h7r-ch8p
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-jqr7-5h7r-ch8p
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.2.0 <5.3.7

## Details
A non-persistent Cross-Site Scripting (XSS) vulnerability has been identified in the Shopware eCommerce platform within the frontend. This vulnerability may allow an attacker to inject and execute malicious scripts in the context of a victim's web browser.

## References
- https://github.com/shopware5/shopware/commit/54461aa651566dc2701b873fe6bd94589604751b
- https://community.shopware.com/_detail_2048.html
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-01-2018?category=shopware-5-en/security-updates
- https://github.com/FriendsOfPHP/security-advisories/blob/master/shopware/shopware/2018-01-22.yaml
- https://github.com/shopware5/shopware
