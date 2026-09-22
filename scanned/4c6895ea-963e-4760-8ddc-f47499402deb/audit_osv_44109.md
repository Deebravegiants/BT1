# [M] Nuclio: Kaniko build tempDir command injection

## Summary
Severity: Medium
Advisory: CVE-2026-79754
Aliases: GHSA-x44h-qmrv-mh72
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-79754
Type: osv

## Details
Nuclio is a "Serverless" framework for Real-Time Events and Data Processing. From version 1.6.19 to before version 1.17.2, Nuclio's Dashboard build pipeline does not sanitize the spec.build.tempDir field before using it to construct a shell command. When the Kaniko container builder is enabled, a user with function-create permission can inject shell metacharacters into this field and achieve arbitrary command execution inside the Dashboard container, which runs with a Kubernetes service account holding wildcard access to Secrets, Pods, Jobs, and Deployments in its namespace. This issue has been patched in version 1.17.2.

## References
- https://github.com/nuclio/nuclio/releases/tag/1.17.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79754.json
- https://github.com/nuclio/nuclio/security/advisories/GHSA-x44h-qmrv-mh72
- https://nvd.nist.gov/vuln/detail/CVE-2026-79754
- https://github.com/nuclio/nuclio/commit/e3ed7de65c20c270a2035b7c27b25800e5b1e252
- https://github.com/nuclio/nuclio/pull/4190
