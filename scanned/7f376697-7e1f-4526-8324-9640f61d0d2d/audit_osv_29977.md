# [H] CVE-2024-48325

## Summary
Severity: High
Advisory: CVE-2024-48325
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-11-06
Source: https://osv.dev/vulnerability/CVE-2024-48325
Type: osv

## Details
Portabilis i-Educar 2.8.0 is vulnerable to SQL Injection in the "getDocuments" function of the "InstituicaoDocumentacaoController" class. The "instituicao_id" parameter in "/module/Api/InstituicaoDocumentacao?oper=get&resource=getDocuments&instituicao_id" is not properly sanitized, allowing an unauthenticated remote attacker to inject malicious SQL commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48325.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48325
- https://github.com/osvaldotenorio/cve-2024-48325
