# [M] HashiCorp Consul can use cleartext agent-to-agent RPC communication

## Summary
Severity: Medium
Advisory: GHSA-4qvx-qq5w-695p
CVE: CVE-2018-19653
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4qvx-qq5w-695p
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0.5.1 <1.4.1

## Details
HashiCorp Consul 0.5.1 through 1.4.0 can use cleartext agent-to-agent RPC communication because the `verify_outgoing` setting is improperly documented. NOTE: the vendor has provided reconfiguration steps that do not require a software upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19653
- https://github.com/hashicorp/consul/pull/5069
- https://github.com/hashicorp/consul/commit/b64e8b262f80397eab4f39c6ae7e14683cb9f55c
- https://github.com/hashicorp/consul
- https://groups.google.com/forum/#!topic/consul-tool/7TCw06oio0I
