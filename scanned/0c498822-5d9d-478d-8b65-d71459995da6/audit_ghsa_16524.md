# [M] silverstripe/userforms file upload exposure on UserForms module

## Summary
Severity: Medium
Advisory: GHSA-55pp-293f-3365
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-55pp-293f-3365
Type: github-advisory

## Affected
- Packagist: `silverstripe/userforms` — affected >=0 <3.0.0

## Details
The [userforms module](https://github.com/silverstripe/silverstripe-userforms) allows CMS administrators to create public facing forms with file upload abilities. These files are uploaded into a predictable public path on the website, unless configured otherwise by the CMS administrator setting up the form. While the name of the uploaded file itself is not predictable, certain actions taken by CMS authors could expose it. For example, submission notification emails contain a link to the file without authorisation checks.

In 3.0.0 this field is disabled by default, but re-enabled upon installation of the [secure assets module](https://github.com/silverstripe-labs/silverstripe-secureassets). When this is installed, the field can once again be used within a form, and will automatically lock this folder to a secure list of users, which can then be configured further by an administrator.

Existing file upload fields will not be disabled, but will require re-enabling via config or installation of secure assets to become editable again.

If any upload field points or is pointed to a folder that is not secured, and the secure assets module is present, then that folder will have the secure permissions applied automatically.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/userforms/SS-2015-018-1.yaml
- https://github.com/silverstripe/silverstripe-userforms
- https://www.silverstripe.org/software/download/security-releases/ss-2015-018
