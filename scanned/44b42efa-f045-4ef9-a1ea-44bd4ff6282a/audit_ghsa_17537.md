# [H] Grafana vulnerable to authenticated users bypassing dashboard, folder permissions

## Summary
Severity: High
Advisory: GHSA-3px7-c4j3-576r
CVE: CVE-2025-3260
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-06-02
Source: https://github.com/advisories/GHSA-3px7-c4j3-576r
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0.0.0-20250114093457-36d6fad421fb <0.0.0-20250521183405-c7a690348df7

## Details
A security vulnerability in the /apis/dashboard.grafana.app/* endpoints allows authenticated users to bypass dashboard and folder permissions. The vulnerability affects all API versions (v0alpha1, v1alpha1, v2alpha1).

Impact:

- Viewers can view all dashboards/folders regardless of permissions

- Editors can view/edit/delete all dashboards/folders regardless of permissions

- Editors can create dashboards in any folder regardless of permissions

- Anonymous users with viewer/editor roles are similarly affected

Organization isolation boundaries remain intact. The vulnerability only affects dashboard access and does not grant access to datasources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3260
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/blob/be8d153dc33734caba4f617ff571d18253e68fa0/CHANGELOG.md#1161-2025-04-23
- https://grafana.com/blog/2025/04/22/grafana-security-release-medium-and-high-severity-fixes-for-cve-2025-3260-cve-2025-2703-cve-2025-3454
- https://grafana.com/security/security-advisories/CVE-2025-3260
