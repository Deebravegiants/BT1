# [H] CVE-2022-3409

## Summary
Severity: High
Advisory: CVE-2022-3409
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-3409
Type: osv

## Details
A vulnerability in bmcweb of OpenBMC Project allows user to cause denial of service. This vulnerability was identified during mitigation for CVE-2022-2809. When fuzzing the multipart_parser code using AFL++ with address sanitizer enabled to find smallest memory corruptions possible. It detected problem in how multipart_parser handles unclosed http headers. If long enough http header is passed in the multipart form without colon there is one byte overwrite on heap. It can be conducted multiple times in a loop to cause DoS.

## References
- https://github.com/openbmc/bmcweb
