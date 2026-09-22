# [H] CVE-2021-43405

## Summary
Severity: High
Advisory: CVE-2021-43405
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-05
Source: https://osv.dev/vulnerability/CVE-2021-43405
Type: osv

## Details
An issue was discovered in FusionPBX before 4.5.30. The fax_extension may have risky characters (it is not constrained to be numeric).

## References
- https://github.com/fusionpbx/fusionpbx/commit/2d2869c1a1e874c46a8c3c5475614ce769bbbd59
- http://packetstormsecurity.com/files/164795/FusionPBX-4.5.29-Remote-Code-Execution.html
