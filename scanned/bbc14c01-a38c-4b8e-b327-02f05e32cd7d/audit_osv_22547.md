# [M] Leak of sensitive information through login page error in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-31143
Aliases: GHSA-6mmq-x3j2-677j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-14
Source: https://osv.dev/vulnerability/CVE-2022-31143
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique and is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. It was found that in affected versions there is an exposure of private information defined in setup of GLPI (like smtp or cas hosts). Note that passwords are not exposed. Users are advised to upgrade to version 10.0.3. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31143.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-6mmq-x3j2-677j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31143
- https://github.com/glpi-project/glpi/commit/e66a0dfe697cbd4b3ec22736a8f8fd025a28f978
