# [H] Authentik Security authentik - Privilege Escalation

## Summary
Severity: High
Advisory: CVE-2026-72534
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72534
Type: osv

## Details
A privilege escalation vulnerability in Authentik Security authentik through 2026.5.6 allows an attacker with a source-scoped SCIM provisioning token to gain superuser privileges by provisioning a SCIM group that matches an existing administrator group by name. The SCIM group ingest function adopts any existing group by name and replaces its membership without validating the source scope against the target group. An attacker can grant their provisioning token full IdP superuser access and lock out all existing administrators.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72534.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72534
- https://github.com/goauthentik/authentik
