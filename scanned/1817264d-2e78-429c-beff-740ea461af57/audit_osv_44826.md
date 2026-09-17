# [M] Snipe-IT before 8.7.1 Denial of Service via Unbounded Note Field

## Summary
Severity: Medium
Advisory: CVE-2026-86734
Aliases: GHSA-4vcv-fc5x-jjwv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86734
Type: osv

## Details
Snipe-IT before 8.7.1 fails to validate the length of the note field in the POST /account/accept/{acceptance} endpoint, allowing authenticated users to submit unbounded input that reaches synchronous CommonMark rendering. Attackers can submit large note values to exhaust PHP worker CPU and cause denial of service through resource exhaustion in the markdown parsing pipeline.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86734.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-4vcv-fc5x-jjwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-86734
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.1-denial-of-service-via-unbounded-note-field
- https://github.com/grokability/snipe-it/commit/66770cfe20cb135e2b7022c7a83d01e6783c914a
