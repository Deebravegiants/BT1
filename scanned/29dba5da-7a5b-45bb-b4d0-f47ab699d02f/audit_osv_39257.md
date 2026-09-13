# [M] Kavita: IDOR in /api/Download/*

## Summary
Severity: Medium
Advisory: CVE-2026-44776
Aliases: GHSA-x3jq-95xw-gwvr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44776
Type: osv

## Details
Kavita is a cross platform reading server. Prior to 0.9.0, the download, size-check, and chapter metadata endpoints do not enforce library-level authorization. A low-privileged user who knows or guesses a chapterId, volumeId, or seriesId belonging to a library they are not assigned to can download the full file contents, query file sizes, and read metadata for that content. This affects /api/Download/volume-size, /api/Download/chapter-size, /api/Download/series-size, /api/Download/volume, /api/Download/chapter, /api/Download/series, and /api/Chapter. This vulnerability is fixed in 0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44776.json
- https://github.com/Kareadita/Kavita/security/advisories/GHSA-x3jq-95xw-gwvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44776
