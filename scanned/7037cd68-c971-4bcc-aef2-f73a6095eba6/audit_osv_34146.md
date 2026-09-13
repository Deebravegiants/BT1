# [H] WeGIA Anonymous Attacker can Delete Arbitrary Image file at endpoint `/html/personalizacao_remover.php`

## Summary
Severity: High
Advisory: CVE-2025-55171
Aliases: GHSA-8rm5-3jvx-hcxv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/CVE-2025-55171
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. Prior to version 3.4.8, the application does not check authentication at endpoint /html/personalizacao_remover.php allowing anonymous attacker (without login) to delete any Image files at endpoint /html/personalizacao_remover.php by defining imagem_0 as image id to delete. This issue has been patched in version 3.4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55171.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-8rm5-3jvx-hcxv
- https://nvd.nist.gov/vuln/detail/CVE-2025-55171
- https://github.com/LabRedesCefetRJ/WeGIA/issues/109
- https://github.com/LabRedesCefetRJ/WeGIA/commit/aa63f499a285bf91795b9836eec0425e7eafe570
