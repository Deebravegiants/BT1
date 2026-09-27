# [M] Nomad Spread Job Stanza May Trigger Panic in Servers

## Summary
Severity: Medium
Advisory: GHSA-6jm6-cmcp-fqjq
CVE: CVE-2022-24684
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-6jm6-cmcp-fqjq
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.9.0 <1.0.18
- Go: `github.com/hashicorp/nomad` — affected >=1.1.0 <1.1.12
- Go: `github.com/hashicorp/nomad` — affected >=1.2.0 <1.2.6

## Details
Nomad and Nomad Enterprise allows operators with job-submit capabilities to use the spread stanza in a way such that it can cause panic in Nomad servers. This vulnerability, CVE-2022-24684, was fixed in Nomad 1.0.18, 1.1.12, and 1.2.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24684
- https://discuss.hashicorp.com/t/hcsec-2022-04-nomad-spread-job-stanza-may-trigger-panic-in-servers
- https://discuss.hashicorp.com/t/hcsec-2022-04-nomad-spread-job-stanza-may-trigger-panic-in-servers/35562
- https://security.netapp.com/advisory/ntap-20220318-0008
- https://www.github.com/hashicorp/nomad
