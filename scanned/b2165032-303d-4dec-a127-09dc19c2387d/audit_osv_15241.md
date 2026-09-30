# [C] CVE-2019-14771

## Summary
Severity: Critical
Advisory: CVE-2019-14771
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-08
Source: https://osv.dev/vulnerability/CVE-2019-14771
Type: osv

## Details
Backdrop CMS 1.12.x before 1.12.8 and 1.13.x before 1.13.3 allows the upload of entire-site configuration archives through the user interface or command line. It does not sufficiently check uploaded archives for invalid data, potentially allowing non-configuration scripts to be uploaded to the server. (This attack is mitigated by the attacker needing the "Synchronize, import, and export configuration" permission, a permission that only trusted administrators should be given. Other preventative measures in Backdrop CMS prevent the execution of PHP scripts, so another server-side scripting language must be accessible on the server to execute code.) Note: This has been disputed by multiple 3rd parties due to advanced permissions that are needed to exploit.

## References
- https://backdropcms.org/security/backdrop-sa-core-2019-012
