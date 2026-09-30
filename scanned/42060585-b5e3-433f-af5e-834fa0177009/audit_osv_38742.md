# [H] Vvveb < 1.0.8.2 XML External Entity Injection via Import

## Summary
Severity: High
Advisory: CVE-2026-41936
Aliases: GHSA-rfxr-4xpm-wrp7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-41936
Type: osv

## Details
Vvveb before version 1.0.8.2 contains an XML external entity (XXE) injection vulnerability in the admin Tools/Import feature that allows authenticated site_admin users to read arbitrary files and modify database records. Attackers can exploit the XML parser configuration in system/import/xml.php to inject file:// or php://filter entity references that are resolved and persisted into the application database, enabling arbitrary file disclosure and administrator password hash overwriting for privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41936.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.2
- https://github.com/givanz/Vvveb/security/advisories/GHSA-rfxr-4xpm-wrp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41936
- https://www.vulncheck.com/advisories/vvveb-xml-external-entity-injection-via-import
- https://github.com/givanz/Vvveb/commit/86f7128a18edebe0ff47e3855558467eb0ef9106
