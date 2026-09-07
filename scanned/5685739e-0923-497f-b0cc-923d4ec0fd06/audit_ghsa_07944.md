# [M] Phraseanet vulnerable to stored cross-site scripting through crafted file names

## Summary
Severity: Medium
Advisory: GHSA-gcpq-mrgg-v5f3
CVE: CVE-2018-25157
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-gcpq-mrgg-v5f3
Type: github-advisory

## Affected
- Packagist: `phraseanet/phraseanet` — affected 4.0.3

## Details
Phraseanet 4.0.3 contains a stored cross-site scripting vulnerability that allows authenticated users to inject malicious scripts through crafted file names during document uploads. Attackers can upload files with embedded SVG scripts that execute in the browser, potentially stealing cookies or redirecting users when the file is viewed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25157
- https://github.com/alchemy-fr/Phraseanet
- https://www.exploit-db.com/exploits/46935
- https://www.phraseanet.com
- https://www.phraseanet.com/en/download
- https://www.vulncheck.com/advisories/phraseanet-stored-xss-via-document-upload
