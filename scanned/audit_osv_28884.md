# [M] Nextcloud Notes app can be tricked into using a received share created before the user logged in

## Summary
Severity: Medium
Advisory: CVE-2024-37317
Aliases: GHSA-wfqv-cx85-7rjx
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37317
Type: osv

## Details
The Nextcloud Notes app is a distraction free notes taking app for Nextcloud. If an attacker managed to share a folder called `Notes/` with a newly created user before they logged in, the Notes app would use that folder store the personal notes. It is recommended that the Nextcloud Notes app is upgraded to 4.9.3.

## References
- https://hackerone.com/reports/2254151
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37317.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wfqv-cx85-7rjx
- https://nvd.nist.gov/vuln/detail/CVE-2024-37317
- https://github.com/nextcloud/notes/pull/1260
