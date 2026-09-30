# [H] CVE-2021-32297

## Summary
Severity: High
Advisory: CVE-2021-32297
Aliases: GHSA-22x7-vwh9-5w4g, PYSEC-2021-324
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32297
Type: osv

## Details
An issue was discovered in LIEF through 0.11.4. A heap-buffer-overflow exists in the function main located in pe_reader.c. It allows an attacker to cause code Execution.

## References
- https://github.com/lief-project/LIEF/issues/449
