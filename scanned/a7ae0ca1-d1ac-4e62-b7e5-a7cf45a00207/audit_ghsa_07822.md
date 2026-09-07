# [M] Craft CMS has Stored XSS in Table Field via "HTML" Column Type

## Summary
Severity: Medium
Advisory: GHSA-3jh3-prx3-w6wc
CVE: CVE-2026-27126
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-3jh3-prx3-w6wc
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.5.0-RC1 <4.16.19
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.23

## Details
A stored Cross-site Scripting (XSS) vulnerability exists in the `editableTable.twig` component when using the `html` column type. The application fails to sanitize the input, allowing an attacker to execute arbitrary JavaScript when another user views a page with the malicious table field.

## Prerequisites
* An administrator account
* `allowAdminChanges` must be enabled in production, which is [against our security recommendations](https://craftcms.com/knowledge-base/securing-craft#set-allowAdminChanges-to-false-in-production).

## Steps to Reproduce
1. Navigate to **Settings** → **Fields** and create a new field with Type: **Table**
1. Add a **Column Heading** and set **Column Type** to `Single-line text`
    - **Note:** The vulnerable **Column Type** is `html`, but it's not available in the UI dropdown.
1. In **Default Values** section, add a row with the following payload:
    ```html
    <img src=x onerror="alert('XSS')">
    ```
1. Enable `Static Rows`
1. Intercept the **Save Field** request using a proxy tool (e.g., Burp Suite) or use `cURL` directly
1. Modify the request body and change the `types[craft-fields-Table][columns][col3][type]` parameter from `singleline` to `html`
1. Forward the request to save the field
1. Use the field in any object (e.g. user profile fields) → then visit the any user's profile
1. Notice the XSS execution
1. The XSS will also trigger when an administrator attempts to edit this field, as the malicious payload is executed within the field configuration page, too.

## Resources

https://github.com/craftcms/cms/commit/f5d488d9bb6eff7670ed2c2fe30e15692e92c52b

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-3jh3-prx3-w6wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27126
- https://github.com/craftcms/cms/commit/f5d488d9bb6eff7670ed2c2fe30e15692e92c52b
- https://github.com/craftcms/cms
