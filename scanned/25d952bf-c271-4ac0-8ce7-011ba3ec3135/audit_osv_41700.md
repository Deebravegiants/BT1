# [C] NLTK before 3.9.3 Missing Post-Download Integrity Verification

## Summary
Severity: Critical
Advisory: CVE-2026-63310
Aliases: CVE-2026-12259, GHSA-5wp5-5229-5g6q, GHSA-gf32-cmjh-8m9v, PYSEC-2026-3729
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-63310
Type: osv

## Details
NLTK before 3.9.3 fails to verify file integrity after downloading packages and before extraction in the downloader module. Attackers can perform man-in-the-middle attacks or DNS poisoning to inject malicious package contents that are extracted without validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63310.json
- https://github.com/nltk/nltk/security/advisories/GHSA-5wp5-5229-5g6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-63310
- https://www.vulncheck.com/advisories/nltk-before-missing-post-download-integrity-verification
