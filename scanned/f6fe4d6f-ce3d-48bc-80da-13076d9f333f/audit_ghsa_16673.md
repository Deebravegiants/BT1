# [M] silverstripe/framework ReadOnly transformation for formfields exploitable

## Summary
Severity: Medium
Advisory: GHSA-97jm-g33h-f46g
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-97jm-g33h-f46g
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.21
- Packagist: `silverstripe/framework` — affected >=3.2.0 <3.2.6
- Packagist: `silverstripe/framework` — affected >=3.3.0 <3.3.4
- Packagist: `silverstripe/framework` — affected >=3.4.0 <3.4.2

## Details
Form fields returning isReadonly() as true are vulnerable to reflected XSS injections. This includes ReadonlyField, LookupField, HTMLReadonlyField, as well as special purpose fields like TimeField_Readonly. Values submitted to through these form fields are not filtered out from the form session data, and might be shown to the user depending on the form behaviour. For example, form validation errors cause the form to re-render with previously submitted values by default.

SilverStripe forms automatically load values from request data (GET and POST), which enables malicious use of URLs if your form uses these fields and doesn't overwrite data on form construction.

Readonly and disabled form fields are already filtered out in Form->saveInto(), so maliciously submitted data on these fields doesn't make it into the database unless you are accessing form values directly in your saving logic.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/8336cb96b9600dacafa8a525c92662345b52cfae
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-010-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-010
