# [M] OpenShift Console Has a Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-69x5-hjg4-m267
CVE: CVE-2024-7631
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-69x5-hjg4-m267
Type: github-advisory

## Affected
- Go: `github.com/openshift/console` — affected >=0

## Details
A flaw was found in the OpenShift Console, an endpoint for plugins to serve resources in multiple languages: /locales/resources.json. This endpoint's lng and ns parameters are used to construct a filepath in pkg/plugins/handlers unsafely.go#L112 Because of this unsafe filepath construction, an authenticated user can manipulate the path to retrieve any JSON files on the console's pod by using sequences of ../ and valid directory paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7631
- https://access.redhat.com/security/cve/CVE-2024-7631
- https://bugzilla.redhat.com/show_bug.cgi?id=2296053
- https://github.com/openshift/console
- https://pkg.go.dev/vuln/GO-2025-3539
