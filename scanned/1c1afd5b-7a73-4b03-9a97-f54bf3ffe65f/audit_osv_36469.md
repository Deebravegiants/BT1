# [H] WeGIA has a Critical SQL Injection in Atendido_ocorrenciaControle via id_memorando parameter

## Summary
Severity: High
Advisory: CVE-2026-23723
Aliases: GHSA-xfmp-2hf9-gfjp
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2026-23723
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to 3.6.2, an authenticated SQL Injection vulnerability was identified in the Atendido_ocorrenciaControle endpoint via the id_memorando parameter. This flaw allows for full database exfiltration, exposure of sensitive PII, and potential arbitrary file reads in misconfigured environments. This vulnerability is fixed in 3.6.2.

## References
- https://github.com/LabRedesCefetRJ/WeGIA/releases/tag/3.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23723.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xfmp-2hf9-gfjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-23723
- https://github.com/LabRedesCefetRJ/WeGIA/pull/1333
