# [M] FormField with square brackets in field name skips validation

## Summary
Severity: Medium
Advisory: GHSA-7mv4-4xpg-xq44
CVE: CVE-2020-26138
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-7mv4-4xpg-xq44
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <4.7.4

## Details
FileField with array notation skips validation

The FileField class is commonly used for file upload in custom code on a Silverstripe website. This field is designed to be used with a single file upload.

PHP allows for submitting multiple values by adding square brackets to the field name. When this is done to a FileField, it will be coerced into allowing multiple files by using this notation. This is not a supported feature, though nothing is done to prevent this.

In this scenario, validation such as limiting allowed extensions is not applied, and the FileField->saveInto() behaviour is not triggered. If custom controller logic is used to process the file uploads, it might implicitly rely on validation to be provided by the Form system, which is not the case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26138
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2020-26138.yaml
- https://www.silverstripe.org/download/security-releases/cve-2020-26138
