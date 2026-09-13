# [M] Keycloak: manage-clients permission escalates to full realm admin access

## Summary
Severity: Medium
Advisory: GHSA-7xf9-4jfc-wgm4
CVE: CVE-2026-3121
CWE: CWE-266
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-7xf9-4jfc-wgm4
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.6

## Details
A flaw was found in Keycloak. An administrator with `manage-clients` permission can exploit a misconfiguration where this permission is equivalent to `manage-permissions`. This allows the administrator to escalate privileges and gain control over roles, users, or other administrative functions within the realm. This privilege escalation can occur when admin permissions are enabled at the realm level.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3121
- https://github.com/keycloak/keycloak/issues/46719
- https://github.com/keycloak/keycloak/commit/79ab3110a257fb8d6f1a664c916687128094ed01
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-3121
- https://bugzilla.redhat.com/show_bug.cgi?id=2442277
- https://github.com/keycloak/keycloak
