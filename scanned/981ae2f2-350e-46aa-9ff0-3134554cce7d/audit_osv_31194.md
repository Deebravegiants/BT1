# [M] Nokogiri before 1.16.5 libxml2 Dependency Update

## Summary
Severity: Medium
Advisory: CVE-2024-58377
Aliases: GHSA-r95h-9x8f-r3f7
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2024-58377
Type: osv

## Details
Nokogiri versions before 1.16.5 bundle libxml2 2.12.6, which is affected by CVE-2024-34459 in libxml2's xmllint tool. Nokogiri 1.16.5 upgrades the bundled libxml2 to 2.12.7 to address this. Per the maintainers, there is no impact to Nokogiri users because Nokogiri does not provide or expose the xmllint tool where the issue occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58377.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-r95h-9x8f-r3f7
- https://nvd.nist.gov/vuln/detail/CVE-2024-58377
- https://www.vulncheck.com/advisories/nokogiri-before-libxml2-dependency-update
- https://github.com/GNOME/libxml2/commit/2876ac53
