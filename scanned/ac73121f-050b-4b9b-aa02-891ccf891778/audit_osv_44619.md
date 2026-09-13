# [C] WWBN AVideo Authentication Bypass via Non-Expiring video_id_hash

## Summary
Severity: Critical
Advisory: CVE-2026-85154
Aliases: GHSA-59p8-6m2v-gcr5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85154
Type: osv

## Details
WWBN AVideo contains an authentication failure vulnerability where the video_id_hash credential is a non-expiring, non-revocable bearer token that grants full administrator session access to the video owner's account. Attackers who obtain a video_id_hash can replay it indefinitely to authenticate as the video owner with full privileges, and the credential remains valid even after the owner changes their password.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85154.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-59p8-6m2v-gcr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-85154
- https://www.vulncheck.com/advisories/wwbn-avideo-authentication-bypass-via-non-expiring-video-id-hash
