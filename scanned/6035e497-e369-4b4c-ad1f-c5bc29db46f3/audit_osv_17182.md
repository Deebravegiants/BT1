# [M] CVE-2020-13496

## Summary
Severity: Medium
Advisory: CVE-2020-13496
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-13496
Type: osv

## Details
An exploitable vulnerability exists in the way Pixar OpenUSD 20.05 handles parses certain encoded types. A specially crafted malformed file can trigger an arbitrary out of bounds memory access in TfToken Type Index. This vulnerability could be used to bypass mitigations and aid further exploitation. To trigger this vulnerability, the victim needs to access an attacker-provided malformed file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1105
