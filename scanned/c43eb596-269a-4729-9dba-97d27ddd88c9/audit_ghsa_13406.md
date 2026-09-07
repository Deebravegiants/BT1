# [M] @vendure/admin-ui-plugin authenticated Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gm68-572p-q28r
CWE: CWE-79
Ecosystem: npm
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-gm68-572p-q28r
Type: github-advisory

## Affected
- npm: `@vendure/admin-ui-plugin` — affected >=0 <2.0.3

## Details
### Impact
Vendure provides an authorization system with different levels of privileges. For example, an administrator cannot create another administrator.

In the admin UI, there are a couple of places with description inputs, such as inventory/collection catalog, shipping methods, promotions, and more.

While the WYSIWYG editor allows limited customization, altering the request data (not in the ui) saves and returns arbitrary HTML with no sanitization. Causing an XSS when viewing the page.

The impact of this XSS is privilege escalation. A user that can write any type of description can trigger the attack. Then any other user that visits the vulnerable page is prone to arbitrary Javascript code execution, giving the attacker ability to execute actions on behalf of this user.

### Patches
in progress

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/vendure-ecommerce/vendure/security/advisories/GHSA-gm68-572p-q28r
- https://github.com/vendure-ecommerce/vendure/commit/0cdc92b241e6fd4017ddfc9fbdca189fc7c1ada0
- https://github.com/vendure-ecommerce/vendure
- https://github.com/vendure-ecommerce/vendure/blob/master/CHANGELOG.md#203-2023-07-04
