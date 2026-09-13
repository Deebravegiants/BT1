# [C] OPNsense: RCE via XMLRPC endpoint using `opnsense.restore_config_section` method

## Summary
Severity: Critical
Advisory: CVE-2026-44193
Aliases: GHSA-xxp9-93cr-x54p
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44193
Type: osv

## Details
OPNsense is a FreeBSD based firewall and routing platform. Prior to 26.1.7, the XMLRPC method opnsense.restore_config_section fails to sanitize user supplied input leading to Remote Code Execution. This vulnerability is fixed in 26.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44193.json
- https://github.com/opnsense/core/security/advisories/GHSA-xxp9-93cr-x54p
- https://nvd.nist.gov/vuln/detail/CVE-2026-44193
