# [H] Rocket.Chat: Authenticated Arbitrary Data Export Theft via Mass Assignment in sendFileMessage

## Summary
Severity: High
Advisory: CVE-2026-45687
Aliases: GHSA-fhc2-x8cp-c5ch
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-45687
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11, Rocket.Chat's sendFileMessage DDP method passes the entire attacker-supplied file object into Uploads.updateFileComplete, which merges it directly into a MongoDB $set update via Object.assign. There is no allow-list of writable fields. An attacker can therefore rewrite any column on their own upload record, notably store and the store-specific path fields. This vulnerability is fixed in 8.5.0, 8.4.1, 8.3.3, 8.2.3, 8.1.4, 8.0.5, 7.13.7, and 7.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45687.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-fhc2-x8cp-c5ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-45687
