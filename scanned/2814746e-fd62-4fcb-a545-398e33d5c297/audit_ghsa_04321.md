# [C] Openshift Migration Advisor: Improper input sanitization allows specially crafted RVTools .xlsx files to include malicious SQL commands

## Summary
Severity: Critical
Advisory: GHSA-vf2h-7x3w-97fr
CVE: CVE-2026-53474
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-vf2h-7x3w-97fr
Type: github-advisory

## Affected
- Go: `github.com/kubev2v/migration-planner` — affected >=0 <0.13.5

## Details
A flaw was found in migration-planner. A remote authenticated attacker could exploit this vulnerability by uploading a specially crafted RVTools .xlsx file. Due to improper input sanitization, malicious SQL embedded within a spreadsheet cell is executed when cluster names are processed. This SQL Injection allows for arbitrary file reading on the system, potentially exposing sensitive information such as Kubernetes service account tokens and other credentials, which could lead to a full compromise of the SaaS environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53474
- https://github.com/kubev2v/migration-planner/pull/1231
- https://github.com/kubev2v/migration-planner/commit/6110711b1b71bb0d15348b934a490a5932b41f83
- https://access.redhat.com/security/cve/CVE-2026-53474
- https://bugzilla.redhat.com/show_bug.cgi?id=2487231
- https://github.com/kubev2v/migration-planner
