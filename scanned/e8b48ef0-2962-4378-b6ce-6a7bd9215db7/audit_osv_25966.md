# [H] Unauthenticated heap buffer overflow in Gorrila codec decompression

## Summary
Severity: High
Advisory: CVE-2023-48704
Aliases: GHSA-5rmf-5g48-xv63
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-48704
Type: osv

## Details
ClickHouse is an open-source column-oriented database management system that allows generating analytical data reports in real-time. A heap buffer overflow issue was discovered in ClickHouse server. An attacker could send a specially crafted payload to the native interface exposed by default on port 9000/tcp, triggering a bug in the decompression logic of Gorilla codec that crashes the ClickHouse server process. This attack does not require authentication. This issue has been addressed in ClickHouse Cloud version 23.9.2.47551 and ClickHouse versions 23.10.5.20, 23.3.18.15, 23.8.8.20, and 23.9.6.20.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48704.json
- https://github.com/ClickHouse/ClickHouse/security/advisories/GHSA-5rmf-5g48-xv63
- https://nvd.nist.gov/vuln/detail/CVE-2023-48704
- https://github.com/ClickHouse/ClickHouse/pull/57107
