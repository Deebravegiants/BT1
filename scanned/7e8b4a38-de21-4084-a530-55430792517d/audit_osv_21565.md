# [H] CVE-2021-44081

## Summary
Severity: High
Advisory: CVE-2021-44081
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2021-44081
Type: osv

## Details
A buffer overflow vulnerability exists in the AMF of open5gs 2.1.4. When the length of MSIN in Supi exceeds 24 characters, it leads to AMF denial of service.

## References
- https://github.com/open5gs/open5gs/issues/1206
