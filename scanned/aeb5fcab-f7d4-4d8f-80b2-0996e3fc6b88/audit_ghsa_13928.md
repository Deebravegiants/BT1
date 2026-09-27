# [C] AVideo contains Command injection when embedding a video link

## Summary
Severity: Critical
Advisory: GHSA-pgvh-p3g4-86jw
CVE: CVE-2023-25313
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-pgvh-p3g4-86jw
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <12.4

## Details
Impact:

An attacker could execute remote code on a system running wwbn/avideo

Step to Reproduce:

1. Go to the `My Videos` tab

https://demo.avideo.com/mvideos

2. Click "Embed a video link"

Append a command to the url as a query string. eg. `?whoami`


then click Save

This issue has been resolved in commit `236228f15`

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pgvh-p3g4-86jw
- https://nvd.nist.gov/vuln/detail/CVE-2023-30842
- https://github.com/WWBN/AVideo/commit/236228f15a9a31be5a0e60f05dac043682e49a5e
- https://github.com/WWBN/AVideo
