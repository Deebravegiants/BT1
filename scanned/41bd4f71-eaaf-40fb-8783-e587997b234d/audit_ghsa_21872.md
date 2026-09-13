# [M] Hashicorp Nomad Information Exposure Through Environmental Variables

## Summary
Severity: Medium
Advisory: GHSA-6hv3-7c34-4hx8
CVE: CVE-2019-14802
CWE: CWE-200, CWE-526
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-6hv3-7c34-4hx8
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <0.9.5

## Details
In Nomad before version 0.9.5, when rendering a task template, all environment variables were available to the rendering task.  As a fix, only task environment variables are used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14802
- https://github.com/hashicorp/nomad/pull/6055
- https://github.com/hashicorp/nomad/commit/e8238305ef0b9ef37be3efd86a8d34bfbed5f63f
- https://advisories.gitlab.com/advisory/advgo_github_com_hashicorp_nomad_client_allocrunner_taskrunner_template_GMS_2022_818.html
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-14802
- https://github.com/hashicorp/nomad
- https://github.com/hashicorp/nomad/releases/tag/v0.9.5
- https://www.hashicorp.com/blog/category/nomad
