# [H] WeGIA < 3.9.2 Authorization Bypass Password Change via alterarSenha

## Summary
Severity: High
Advisory: CVE-2026-76633
Aliases: GHSA-gfcx-7973-hjmp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76633
Type: osv

## Details
WeGIA before 3.9.2 contains an authorization bypass vulnerability in the password change flow that allows any authenticated user to change their account password without providing existing credentials by exploiting the unconditional exclusion of the alterarSenha method from permission checks in controle/control.php. Attackers can manipulate the redir parameter to point to alterar_senha.php, routing through verificarSenhaConfig() instead of verificarSenha() to bypass current password verification and convert temporary session access into permanent account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76633.json
- https://github.com/LabRedesCefetRJ/WeGIA/releases#release-3.9.2
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-gfcx-7973-hjmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-76633
- https://www.vulncheck.com/advisories/wegia-authorization-bypass-password-change-via-alterarsenha
- https://github.com/LabRedesCefetRJ/WeGIA
