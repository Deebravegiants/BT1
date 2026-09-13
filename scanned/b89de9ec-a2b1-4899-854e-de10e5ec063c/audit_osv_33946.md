# [M] GLPI's MailCollector Receiver is vulnerable to credential exfiltration

## Summary
Severity: Medium
Advisory: CVE-2025-53008
Aliases: GHSA-52h8-76ph-4j9q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-53008
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. In versions 9.3.1 through 10.0.19, a connected user can use a malicious payload to steal mail receiver credentials. This is fixed in version 10.0.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53008.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-52h8-76ph-4j9q
- https://nvd.nist.gov/vuln/detail/CVE-2025-53008
