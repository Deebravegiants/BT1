# [M] CVE-2020-13495

## Summary
Severity: Medium
Advisory: CVE-2020-13495
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2020-13495
Type: osv

## Details
An exploitable vulnerability exists in the way Pixar OpenUSD 20.05 handles file offsets in binary USD files. A specially crafted malformed file can trigger an arbitrary out-of-bounds memory access that could lead to the disclosure of sensitive information. This vulnerability could be used to bypass mitigations and aid additional exploitation. To trigger this vulnerability, the victim needs to access an attacker-provided file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1104
