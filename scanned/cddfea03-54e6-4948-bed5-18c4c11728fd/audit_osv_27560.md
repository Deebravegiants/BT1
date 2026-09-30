# [M] Uploading an image with a specific filename causes a server-side DoS

## Summary
Severity: Medium
Advisory: CVE-2024-23826
Aliases: GHSA-5vfc-v7hg-pvwm
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2024-23826
Type: osv

## Details
spbu_se_site is the website of the Department of System Programming of St. Petersburg State University. Before 2024.01.29, when uploading an avatar image, an authenticated user may intentionally use a large Unicode filename which would lead to a server-side denial of service under Windows. This is due to no limitation of the length of the filename and the costly use of the Unicode normalization with the form NFKD on Windows OS.  This vulnerability was fixed in the 2024.01.29 release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23826.json
- https://github.com/spbu-se/spbu_se_site/security/advisories/GHSA-5vfc-v7hg-pvwm
- https://nvd.nist.gov/vuln/detail/CVE-2024-23826
- https://github.com/spbu-se/spbu_se_site/commit/5ad623eb0405260763046343c5785bc588d8a57d
