# [H] cart2quote/module-quotation-encoded Remote Code Execution via downloadCustomOptionAction

## Summary
Severity: High
Advisory: GHSA-pgj4-g5j4-cmfx
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-pgj4-g5j4-cmfx
Type: github-advisory

## Affected
- Packagist: `cart2quote/module-quotation-encoded` — affected >=4.1.6
- Packagist: `cart2quote/module-quotation-encoded` — affected >=5.0.0 <5.4.4

## Details
cart2quote/module-quotation-encoded extension may expose a critical security vulnerability by utilizing the unserialize function when processing data from a GET request. This flaw, present in the app/code/community/Ophirah/Qquoteadv/controllers/DownloadController.php and app/code/community/Ophirah/Qquoteadv/Helper/Data.php files, poses a significant risk of Remote Code Execution, especially when custom file options are employed on a product. Attackers exploiting this vulnerability could execute arbitrary code remotely, leading to unauthorized access and potential compromise of sensitive data.

## References
- https://bitbucket.org/cart2quote2/cart2quote2-releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cart2quote/module-quotation/2017-02-01.yaml
- https://web.archive.org/web/20230131172111/https://cart2quote.zendesk.com/hc/en-us/articles/115000616303--FIXED-Security-Vulnerability-in-downloadCustomOptionAction
