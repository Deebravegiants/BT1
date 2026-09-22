# [H] Server-Side Request Forgery (SSRF) in Chamilo LMS

## Summary
Severity: High
Advisory: CVE-2026-31941
Aliases: GHSA-q74c-mx8x-489h
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-31941
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, Chamilo LMS contains a Server-Side Request Forgery (SSRF) vulnerability in the Social Wall feature. The endpoint read_url_with_open_graph accepts a URL from the user via the social_wall_new_msg_main POST parameter and performs two server-side HTTP requests to that URL without validating whether the target is an internal or external resource. This allows an authenticated attacker to force the server to make arbitrary HTTP requests to internal services, scan internal ports, and access cloud instance metadata. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31941.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-q74c-mx8x-489h
- https://nvd.nist.gov/vuln/detail/CVE-2026-31941
- https://github.com/chamilo/chamilo-lms/commit/e3790c5f0ff3b4dc547c2099fadf5c438c1bb265
- https://github.com/chamilo/chamilo-lms/commit/ea6b7b7e90580c9b01dc4bcafe4ad737061e0ead
