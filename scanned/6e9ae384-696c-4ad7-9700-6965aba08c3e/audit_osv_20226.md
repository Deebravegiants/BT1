# [M] CVE-2021-32289

## Summary
Severity: Medium
Advisory: CVE-2021-32289
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32289
Type: osv

## Details
An issue was discovered in heif through through v3.6.2. A NULL pointer dereference exists in the function convertByteStreamToRBSP() located in nalutil.cpp. It allows an attacker to cause Denial of Service.

## References
- https://github.com/nokiatech/heif/issues/85
