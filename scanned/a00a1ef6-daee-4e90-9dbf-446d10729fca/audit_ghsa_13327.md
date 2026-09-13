# [M] Hashicorp Nomad ACLs Cannot Deny Access to Workload’s Own Variables

## Summary
Severity: Medium
Advisory: GHSA-hhvx-8755-4cvw
CVE: CVE-2023-1296
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-hhvx-8755-4cvw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.4.0 <1.4.6
- Go: `github.com/hashicorp/nomad` — affected >=1.5.0 <1.5.1

## Details
A vulnerability was identified in Nomad and Nomad Enterprise (“Nomad”) such that a deny ACL capability could not be applied to a workload’s own variables. If included, the Nomad ACL system will silently fail to block access. This vulnerability, CVE-2023-1296, was fixed in Nomad 1.4.6 and 1.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1296
- https://discuss.hashicorp.com/t/hcsec-2023-09-nomad-acls-can-not-deny-access-to-workloads-own-variables/51390
- https://github.com/hashicorp/nomad
