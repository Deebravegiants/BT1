# [M] Phishing through a login page malicious URL in GLPI

## Summary
Severity: Medium
Advisory: CVE-2023-41888
Aliases: GHSA-2hcg-75jj-hghp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-41888
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. The lack of path filtering on the GLPI URL may allow an attacker to transmit a malicious URL of login page that can be used to attempt a phishing attack on user credentials. Users are advised to upgrade to version 10.0.10. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41888.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-2hcg-75jj-hghp
- https://nvd.nist.gov/vuln/detail/CVE-2023-41888
