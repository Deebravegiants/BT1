# [H] CVE-2024-29672

## Summary
Severity: High
Advisory: CVE-2024-29672
CVSS: 8.8 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:N/S:U/UI:R)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-29672
Type: osv

## Details
Directory Traversal vulnerability in zly2006 Reden before v.0.2.514 allows a remote attacker to execute arbitrary code via the DEBUG_RTC_REQUEST_SYNC_DATA in KeyCallbacks.kt.

## References
- https://gist.github.com/apple502j/193358682885fe1a6708309ce934e4ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29672.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29672
- https://github.com/zly2006/reden-is-what-we-made/commit/44c5320f0a1ccaa764dd91df6a12e747f81fe63a
