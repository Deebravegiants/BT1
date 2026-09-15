# [C] WeGIA allows SQL Injection in html/funcionario/profile_funcionario.php (id_funcionario parameter)

## Summary
Severity: Critical
Advisory: CVE-2025-53529
Aliases: GHSA-rrj6-pj6w-8j2r
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53529
Type: osv

## Details
WeGIA is a web manager for charitable institutions. An SQL Injection vulnerability was identified in the /html/funcionario/profile_funcionario.php endpoint. The id_funcionario parameter is not properly sanitized or validated before being used in a SQL query, allowing an unauthenticated attacker to inject arbitrary SQL commands. The vulnerability is fixed in 3.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53529.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-rrj6-pj6w-8j2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-53529
- https://github.com/LabRedesCefetRJ/WeGIA/commit/0a061bcc5024937edd18ab3e65ccc8f38deb6957
