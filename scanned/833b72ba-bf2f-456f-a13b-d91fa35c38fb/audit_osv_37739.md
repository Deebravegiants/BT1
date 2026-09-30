# [C] FastGPT has Arbitrary Code Execution in GitHub Actions via pull_request_target in fastgpt-preview-image.yml

## Summary
Severity: Critical
Advisory: CVE-2026-33075
Aliases: GHSA-xfx8-w35j-485c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33075
Type: osv

## Details
FastGPT is an AI Agent building platform. In versions 4.14.8.3 and below, the fastgpt-preview-image.yml workflow is vulnerable to arbitrary code execution and secret exfiltration by any external contributor. It uses pull_request_target (which runs with access to repository secrets) but checks out code from the pull request author's fork, then builds and pushes Docker images using attacker-controlled Dockerfiles. This also enables a supply chain attack via the production container registry. A patch was not available at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33075.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-xfx8-w35j-485c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33075
