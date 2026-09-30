# [M] CVE-2020-13494

## Summary
Severity: Medium
Advisory: CVE-2020-13494
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-13494
Type: osv

## Details
A heap overflow vulnerability exists in the Pixar OpenUSD 20.05 parsing of compressed string tokens in binary USD files. A specially crafted malformed file can trigger a heap overflow which can result in out of bounds memory access which could lead to information disclosure. This vulnerability could be used to bypass mitigations and aid further exploitation. To trigger this vulnerability, victim needs to access an attacker-provided malformed file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1103
