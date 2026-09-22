# [C] CVE-2016-10105

## Summary
Severity: Critical
Advisory: CVE-2016-10105
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-03
Source: https://osv.dev/vulnerability/CVE-2016-10105
Type: osv

## Details
admin/plugin.php in Piwigo through 2.8.3 doesn't validate the sections variable while using it to include files. This can cause information disclosure and code execution if it contains a .. sequence.

## References
- http://www.securityfocus.com/bid/95202
- https://github.com/Piwigo/Piwigo/commit/8796e43aa344681d92a92e1f9b985409d4f36e31
- https://github.com/Piwigo/Piwigo/commit/9004fdfc0b4a11cb32e9e15a5f67e4ec827e82dc
- https://github.com/Piwigo/Piwigo/issues/574#issuecomment-267938358
