# [C] Duck Site: Untrusted pull request code can trigger privileged production deployment

## Summary
Severity: Critical
Advisory: CVE-2026-47174
Aliases: GHSA-qj93-7xrg-rvhw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47174
Type: osv

## Details
In Duck Site before version 1.0.1, the repository has a deploy workflow that runs after the build workflow completes. The build workflow runs on pull requests, while the deploy workflow runs with package-write permissions and deployment secrets. If an attacker can make a pull request build satisfy the deploy workflow’s main branch condition, the deploy job checks out the triggering workflow commit, builds it into a Docker image, pushes it as latest, and triggers Dokploy deployment. This can allow attacker-controlled pull request code to become the deployed production site image without being merged. This issue has been patched in version 1.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47174.json
- https://github.com/duck-organization/duck-site/security/advisories/GHSA-qj93-7xrg-rvhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-47174
