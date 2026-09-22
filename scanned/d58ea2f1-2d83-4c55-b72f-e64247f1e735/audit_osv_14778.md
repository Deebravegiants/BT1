# [H] CVE-2019-11407

## Summary
Severity: High
Advisory: CVE-2019-11407
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-17
Source: https://osv.dev/vulnerability/CVE-2019-11407
Type: osv

## Details
app/operator_panel/index_inc.php in the Operator Panel module in FusionPBX 4.4.3 suffers from an information disclosure vulnerability due to excessive debug information, which allows authenticated administrative attackers to obtain credentials and other sensitive information.

## References
- https://blog.gdssecurity.com/labs/2019/6/7/rce-using-caller-id-multiple-vulnerabilities-in-fusionpbx.html
- https://github.com/fusionpbx/fusionpbx/commit/f38676b7b63bb1ec3a68d577fe23e6701f482aef
