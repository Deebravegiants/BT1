# [H] GHSL-2023-255: HertzBeat Authenticated (user role) RCE via unsafe deserialization in /api/monitors/import

## Summary
Severity: High
Advisory: CVE-2024-42362
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-42362
Type: osv

## Details
Hertzbeat is an open source, real-time monitoring system. Hertzbeat has an authenticated (user role) RCE via unsafe deserialization in /api/monitors/import. This vulnerability is fixed in 1.6.0.

## References
- https://github.com/apache/hertzbeat/pull/1620/files#diff-9c5fb3d1b7e3b0f54bc5c4182965c4fe1f9023d449017cece3005d3f90e8e4d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42362.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42362
- https://securitylab.github.com/advisories/GHSL-2023-254_GHSL-2023-256_HertzBeat/
- https://github.com/apache/hertzbeat/commit/79f5408e345e8e89da97be05f43e3204a950ddfb
- https://github.com/apache/hertzbeat/commit/9dbbfb7812fc4440ba72bdee66799edd519d06bb
- https://github.com/apache/hertzbeat/pull/1611
- https://github.com/apache/hertzbeat/pull/1620
