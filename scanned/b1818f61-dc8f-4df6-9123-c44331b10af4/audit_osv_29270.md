# [M] Puncia Cleartext Transmission of Sensitive Information via HTTP urls in `API_URLS`

## Summary
Severity: Medium
Advisory: CVE-2024-41124
Aliases: GHSA-rwcj-7jjp-4w38, PYSEC-2026-1809
CVSS: 6.3 (CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-41124
Type: osv

## Details
Puncia is the Official CLI utility for Subdomain Center & Exploit Observer. `API_URLS` is utilizing HTTP instead of HTTPS for communication that can lead to issues like Eavesdropping, Data Tampering, Unauthorized Data Access & MITM Attacks. This issue has been addressed in release version 0.21 by using https rather than http connections. All users are advised to upgrade. There is no known workarounds for this vulnerability.

## References
- https://github.com/ARPSyndicate/puncia/security/advisories/GHSA-rwcj-7jjp-4w38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41124.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41124
- https://github.com/ARPSyndicate/puncia/issues/8
- https://github.com/ARPSyndicate/puncia/commit/033f3b68126eabbb2040ce16e2c3a2ce17437fbd#diff-3ec6c2de51e702726b23c452e3f4a899f6f4253af9fbf5be7254a5c1407ab526
