# [H] CVE-2016-9184

## Summary
Severity: High
Advisory: CVE-2016-9184
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-9184
Type: osv

## Details
In /framework/modules/core/controllers/expHTMLEditorController.php of Exponent CMS 2.4.0, untrusted input is used to construct a table name, and in the selectObject method in mysqli class, table names are wrapped with a character that common filters do not filter, allowing for SQL Injection. Impact is Information Disclosure.

## References
- http://www.securityfocus.com/bid/94227
- https://github.com/exponentcms/exponent-cms/commit/0ce8b94d745b818bd207933d9a2e7f32587c2c89
