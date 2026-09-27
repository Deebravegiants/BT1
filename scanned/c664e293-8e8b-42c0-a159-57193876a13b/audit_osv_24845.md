# [H] CVE-2023-27587

## Summary
Severity: High
Advisory: CVE-2023-27587
Aliases: GHSA-23g5-r34j-mr8g
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2023-03-13
Source: https://osv.dev/vulnerability/CVE-2023-27587
Type: osv

## Details
ReadtoMyShoe, a web app that lets users upload articles and listen to them later, generates an error message containing sensitive information prior to commit 8533b01. If an error occurs when adding an article, the website shows the user an error message. If the error originates from the Google Cloud TTS request, then it will include the full URL of the request. The request URL contains the Google Cloud API key. This has been patched in commit 8533b01. Upgrading should be accompanied by deleting the current GCP API key and issuing a new one. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27587.json
- https://github.com/rozbb/readtomyshoe/security/advisories/GHSA-23g5-r34j-mr8g
- https://nvd.nist.gov/vuln/detail/CVE-2023-27587
- https://github.com/rozbb/readtomyshoe/commit/8533b01c818939a0fa919c7244d8dbf5daf032af
