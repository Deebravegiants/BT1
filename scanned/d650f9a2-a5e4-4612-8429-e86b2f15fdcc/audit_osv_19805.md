# [H] CVE-2021-25966

## Summary
Severity: High
Advisory: CVE-2021-25966
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-10
Source: https://osv.dev/vulnerability/CVE-2021-25966
Type: osv

## Details
In “Orchard core CMS” application, versions 1.0.0-beta1-3383 to 1.0.0 are vulnerable to an improper session termination after password change. When a password has been changed by the user or by an administrator, a user that was already logged in, will still have access to the application even after the password was changed.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25966
- https://github.com/OrchardCMS/OrchardCore/blob/v1.0.0/src/OrchardCore.Modules/OrchardCore.Users/Controllers/ResetPasswordController.cs#L123
