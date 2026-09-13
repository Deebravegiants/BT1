# [H] h2o has HTTP/2 state amplification

## Summary
Severity: High
Advisory: CVE-2026-54340
Aliases: GHSA-qcrr-wrhc-pgq9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-54340
Type: osv

## Details
h2o is an HTTP server with support for HTTP/1.x, HTTP/2 and HTTP/3. Prior to commit 9265bdd, there is an HTTP/2 state amplification issue that combines HPACK decompression amplification with Slowloris-style stream stalling. Amplified decoded header state can be retained by stalled HTTP/2 streams, and depending on the configuration, additional limits are needed to bound decoded header state and prevent attack. This issue has been fixed by commit 9265bdd.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54340.json
- https://github.com/h2o/h2o/security/advisories/GHSA-qcrr-wrhc-pgq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-54340
- https://github.com/h2o/h2o/commit/9265bdd9a996ed992681055e3996baf3e09d2063
