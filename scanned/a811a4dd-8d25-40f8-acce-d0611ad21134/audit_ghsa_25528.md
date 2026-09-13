# [H] Hashicorp Consul HTTP health check endpoints returning an HTTP redirect may be abused as SSRF vector

## Summary
Severity: High
Advisory: GHSA-q6h7-4qgw-2j9p
CVE: CVE-2022-29153
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-q6h7-4qgw-2j9p
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.9.17
- Go: `github.com/hashicorp/consul` — affected >=1.10.0 <1.10.10
- Go: `github.com/hashicorp/consul` — affected >=1.11.0 <1.11.5

## Details
A vulnerability was identified in Consul and Consul Enterprise (“Consul”) such that HTTP health check endpoints returning an HTTP redirect may be abused as a vector for server-side request forgery (SSRF). This vulnerability, CVE-2022-29153, was fixed in Consul 1.9.17, 1.10.10, and 1.11.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29153
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-10-consul-s-http-health-check-may-allow-server-side-request-forgery
- https://discuss.hashicorp.com/t/hcsec-2022-10-consul-s-http-health-check-may-allow-server-side-request-forgery/38393
- https://github.com/hashicorp/consul
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RBODKZL7HQE5XXS3SA2VIDVL4LAA5RWH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBODKZL7HQE5XXS3SA2VIDVL4LAA5RWH
- https://security.gentoo.org/glsa/202208-09
- https://security.netapp.com/advisory/ntap-20220602-0005
