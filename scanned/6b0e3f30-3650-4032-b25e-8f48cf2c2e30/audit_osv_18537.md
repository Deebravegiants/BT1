# [C] CVE-2020-28468

## Summary
Severity: Critical
Advisory: CVE-2020-28468
Aliases: GHSA-7xc5-ggpp-g249, PYSEC-2021-72, SNYK-PYTHON-PWNTOOLS-1047345
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2020-28468
Type: osv

## Details
This affects the package pwntools before 4.3.1. The shellcraft generator for affected versions of this module are vulnerable to Server-Side Template Injection (SSTI), which can lead to remote code execution.

## References
- https://github.com/Gallopsled/pwntools/issues/1427
- https://github.com/Gallopsled/pwntools/pull/1732
- https://snyk.io/vuln/SNYK-PYTHON-PWNTOOLS-1047345
