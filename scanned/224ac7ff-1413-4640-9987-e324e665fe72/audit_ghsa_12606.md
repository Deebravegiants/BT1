# [H] Hashicorp Consul allows user with service:write permissions to patch remote proxy instances

## Summary
Severity: High
Advisory: GHSA-rqjq-ww83-wv5c
CVE: CVE-2023-2816
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-03
Source: https://github.com/advisories/GHSA-rqjq-ww83-wv5c
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.15.0 <1.15.3

## Details
Consul and Consul Enterprise allowed any user with service:write permissions to use Envoy extensions configured via service-defaults to patch remote proxy instances that target the configured service, regardless of whether the user has permission to modify the service(s) corresponding to those modified proxies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2816
- https://discuss.hashicorp.com/t/hcsec-2023-16-consul-envoy-extension-downstream-proxy-configuration-by-upstream-service-owner/54525
- https://github.com/hashicorp/consul
