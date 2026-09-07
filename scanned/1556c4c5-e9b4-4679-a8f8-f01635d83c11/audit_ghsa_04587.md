# [C] Openshift Migration Advisor: Broken access control in migration-planner image-url endpoint exposes other users' OVA images and agent JWTs

## Summary
Severity: Critical
Advisory: GHSA-v5m8-5455-qw2x
CVE: CVE-2026-53470
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-v5m8-5455-qw2x
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/migration-planner` — affected >=0 <0.13.5

## Details
A flaw was found in migration-planner. An authenticated attacker could exploit an improper access control vulnerability in the `/api/v1/sources/{id}/image-url` endpoint. This flaw allows the attacker to bypass an ownership check and obtain presigned S3 URLs for Open Virtual Appliance (OVA) images belonging to other users. Consequently, the attacker can download OVA images containing sensitive information, such as long-lived agent JSON Web Tokens (JWTs) and source configurations, potentially leading to unauthorized access and modification of the victim's source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53470
- https://github.com/kubev2v/migration-planner/pull/1218
- https://github.com/kubev2v/migration-planner/commit/ec47a336a620f4a995f29c1c53e4e4bd70a26e00
- https://access.redhat.com/security/cve/CVE-2026-53470
- https://bugzilla.redhat.com/show_bug.cgi?id=2487069
- https://github.com/kubev2v/migration-planner
