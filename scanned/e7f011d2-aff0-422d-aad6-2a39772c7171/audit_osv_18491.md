# [H] CVE-2020-27996

## Summary
Severity: High
Advisory: CVE-2020-27996
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/CVE-2020-27996
Type: osv

## Details
An issue was discovered in SmartStoreNET before 4.0.1. It does not properly consider the need for a CustomModelPartAttribute decoration in certain ModelBase.CustomProperties situations.

## References
- https://github.com/smartstore/SmartStoreNET/compare/4.0.0...4.0.1
- https://github.com/smartstore/SmartStoreNET/commit/8702c6140f4fc91956ef35dba12d24492fb3f768
- https://securitylab.github.com/advisories/GHSL-2020-138-139-SmartstoreAG-SmartStoreNET
