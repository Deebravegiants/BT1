# [H] WeGIA vulnerable to SQL Injection into method `excluir` of  the `ProdutoControle` class in the parameter `id_produto`.

## Summary
Severity: High
Advisory: CVE-2025-59939
Aliases: GHSA-jx9m-pgf8-v489
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-27
Source: https://osv.dev/vulnerability/CVE-2025-59939
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. Prior to version 3.5.0, WeGIA is vulnerable to SQL Injection attacks in the control.php endpoint with the following parameters: nomeClasse=ProdutoControle&metodo=excluir&id_produto=[malicious command]. It is necessary to apply prepared statements methods, sanitization, and validations on theid_produto parameter. This issue has been patched in version 3.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59939.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-jx9m-pgf8-v489
- https://nvd.nist.gov/vuln/detail/CVE-2025-59939
