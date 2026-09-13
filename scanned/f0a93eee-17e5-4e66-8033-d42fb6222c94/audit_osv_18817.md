# [H] CVE-2020-36325

## Summary
Severity: High
Advisory: CVE-2020-36325
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2020-36325
Type: osv

## Details
An issue was discovered in Jansson through 2.13.1. Due to a parsing error in json_loads, there's an out-of-bounds read-access bug. NOTE: the vendor reports that this only occurs when a programmer fails to follow the API specification

## References
- https://github.com/akheron/jansson/issues/548
