# [M] BigBlueButton: Presentation URL Security Hardening

## Summary
Severity: Medium
Advisory: CVE-2026-46404
Aliases: GHSA-xqm3-6q7q-4v5h
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46404
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.23, the presentation URL validation did not properly restrict access to site local and link local addresses. The redirect following logic now pins resolved IPs. This issue is fixed in version 3.0.23.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46404.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-xqm3-6q7q-4v5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-46404
- https://github.com/bigbluebutton/bigbluebutton/commit/7ccc60c965d744d9fb637715052352a1e59a2c27
