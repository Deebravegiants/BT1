# [C] CloudPirates Open Source Helm Charts: GitHub Actions pull_request_target workflow allows secret exfiltration via fork pull requests

## Summary
Severity: Critical
Advisory: CVE-2026-45131
Aliases: GHSA-c47r-c7gw-cvph
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45131
Type: osv

## Details
CloudPirates Open Source Helm Charts is a collection of Helm charts. Prior to commit fcf9302, a GitHub Actions workflow (pull-request.yaml) executes attacker-controlled code from fork pull requests in a privileged context, exposing repository secrets including Docker Hub credentials and tokens without requiring maintainer approval. This issue has been patched via commit fcf9302.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45131.json
- https://github.com/CloudPirates-io/helm-charts/security/advisories/GHSA-c47r-c7gw-cvph
- https://nvd.nist.gov/vuln/detail/CVE-2026-45131
- https://github.com/CloudPirates-io/helm-charts/commit/fcf930211604652aec15085895b6457bc8b73b54
