# [C] CloudPirates Open Source Helm Charts: GitHub Actions workflow leaks PAT and SSH signing key via unsafe credential handling

## Summary
Severity: Critical
Advisory: CVE-2026-45132
Aliases: GHSA-r874-j8fr-x2pj
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45132
Type: osv

## Details
CloudPirates Open Source Helm Charts is a collection of Helm charts. Prior to commit fcf9302, a GitHub Actions workflow (generate-schema.yaml) exposes sensitive credentials (Personal Access Token and SSH signing key) to fork-controlled code due to unsafe checkout and credential handling practices. This issue has been patched via commit fcf9302.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45132.json
- https://github.com/CloudPirates-io/helm-charts/security/advisories/GHSA-r874-j8fr-x2pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45132
- https://github.com/CloudPirates-io/helm-charts/commit/fcf930211604652aec15085895b6457bc8b73b54
