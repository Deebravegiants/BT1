# [C] CVE-2020-36364

## Summary
Severity: Critical
Advisory: CVE-2020-36364
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-05-19
Source: https://osv.dev/vulnerability/CVE-2020-36364
Type: osv

## Details
An issue was discovered in Smartstore (aka SmartStoreNET) before 4.1.0. Administration/Controllers/ImportController.cs allows path traversal (for copy and delete actions) in the ImportController.Create method via a TempFileName field.

## References
- https://github.com/smartstore/SmartStoreNET/issues/2112
- https://github.com/smartstore/SmartStoreNET/commit/5ab1e37dc8d6415d04354e1a116f3d82e9555f5c
