# [C] CVE-2020-23907

## Summary
Severity: Critical
Advisory: CVE-2020-23907
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23907
Type: osv

## Details
An issue was discovered in retdec v3.3. In function canSplitFunctionOn() of ir_modifications.cpp, there is a possible out of bounds read due to a heap buffer overflow. The impact is: Deny of Service, Memory Disclosure, and Possible Code Execution.

## References
- https://github.com/avast/retdec/commit/517298bafaaff0a8e3dd60dd055a67c41b545807
- https://github.com/avast/retdec/issues/637
