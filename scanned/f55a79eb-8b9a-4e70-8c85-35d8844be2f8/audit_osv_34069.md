# [C] dag-factory's CI/CD Workflow Allows for Repository Takeover and Secret Exfiltration

## Summary
Severity: Critical
Advisory: CVE-2025-54415
Aliases: GHSA-g5hx-xv45-9whg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:U)
Published: 2025-07-26
Source: https://osv.dev/vulnerability/CVE-2025-54415
Type: osv

## Details
dag-factory is a library for Apache Airflow® to construct DAGs declaratively via configuration files. In versions 0.23.0a8 and below, a high-severity vulnerability has been identified in the cicd.yml workflow within the astronomer/dag-factory GitHub repository. The workflow, specifically when triggered by pull_request_target, is susceptible to exploitation, allowing an attacker to execute arbitrary code within the GitHub Actions runner environment. This misconfiguration enables an attacker to establish a reverse shell, exfiltrate sensitive secrets, including the highly-privileged GITHUB_TOKEN, and ultimately gain full control over the repository. This is fixed in version 0.23.0a9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54415.json
- https://github.com/astronomer/dag-factory/security/advisories/GHSA-g5hx-xv45-9whg
- https://nvd.nist.gov/vuln/detail/CVE-2025-54415
- https://github.com/astronomer/dag-factory/commit/751c0e58369e784f6a924347e381a705ea8133fe
- https://github.com/astronomer/dag-factory/pull/460
- https://github.com/astronomer/dag-factory/pull/466
