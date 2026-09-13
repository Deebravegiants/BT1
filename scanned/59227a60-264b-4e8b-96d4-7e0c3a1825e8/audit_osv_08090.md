# [M] CVE-2016-10215

## Summary
Severity: Medium
Advisory: CVE-2016-10215
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-02-10
Source: https://osv.dev/vulnerability/CVE-2016-10215
Type: osv

## Details
An issue was discovered in Fastspot BigTree bigtree-form-builder before 1.2. The vulnerability exists due to insufficient filtration of user-supplied data in multiple HTTP POST parameters passed to a "site/index.php/../../extensions/com.fastspot.form-builder/ajax/redraw-field.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://github.com/Fastspot/bigtree-form-builder/commit/06fde0cc67ff121b212715031e12574f50970fcd
