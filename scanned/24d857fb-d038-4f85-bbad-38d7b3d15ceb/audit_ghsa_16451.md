# [C] Shopware Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7336-ghhp-f2qj
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-7336-ghhp-f2qj
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.2.15 <5.2.16

## Details
Under certain circumstances, it’s possible to execute an unauthorized foreign code in Shopware in versions prior to 5.2.16. One possible threat is if a template that doesn’t derive from the Shopware standard has been completely copied. Themes or plugins that execute or overwrite the following template code are vulnerable.

- Affected file: emotion.tpl

Path template file "Emotion template": templates / _default / frontend / forms / elements.tpl
Path template file "Responsive template": themes/Frontend/Bare/frontend/forms/elements.tpl

The complete line beginning with: `{eval var=$sSupport.sFields[$sKey]...` should be exchanged with the following:

```
{$sSupport.sFields[$sKey]|replace:'{literal}':''|replace:'{/literal}':''|replace:'%*%':"{s name='RequiredField' namespace='frontend/register/index'}{/s}"}
```

## References
- https://github.com/shopware5/shopware/commit/6113d30a90e626154e438aa896e656c0f38694f3
- https://community.shopware.com/_detail_1989.html
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-01-2017?category=shopware-5-en/security-updates
- https://github.com/FriendsOfPHP/security-advisories/blob/master/shopware/shopware/2017-01-25.yaml
- https://github.com/shopware5/shopware
