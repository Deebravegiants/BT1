# [H] CVE-2025-54955

## Summary
Severity: High
Advisory: CVE-2025-54955
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-02
Source: https://osv.dev/vulnerability/CVE-2025-54955
Type: osv

## Details
OpenNebula Community Edition (CE) before 7.0.0 and Enterprise Edition (EE) before 6.10.3 have a critical FireEdge race condition that can lead to full account takeover. By exploiting this, an unauthenticated attacker can obtain a valid JSON Web Token (JWT) belonging to a legitimate user without knowledge of their credentials.

## References
- https://docs.opennebula.io/6.10/intro_release_notes/release_notes_enterprise/resolved_issues_6103.html
- https://github.com/OpenNebula/one/releases/tag/release-7.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54955.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54955
- https://github.com/OpenNebula/one/commit/81058d9705e7ac619d294423de28b76d88f613b6
- https://github.com/OpenNebula/one
- https://github.com/Stolichnayer/OpenNebula-Account-Takeover
