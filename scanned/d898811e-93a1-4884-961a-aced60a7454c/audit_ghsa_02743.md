# [H] Hashicorp Consul Missing SSL Certificate Validation

## Summary
Severity: High
Advisory: GHSA-25gf-8qrr-g78r
CVE: CVE-2021-32574
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-07-19
Source: https://github.com/advisories/GHSA-25gf-8qrr-g78r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.10.1

## Details
HashiCorp Consul before 1.10.1 (and Consul Enterprise) has Missing SSL Certificate Validation. xds does not ensure that the Subject Alternative Name of an upstream is validated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32574
- https://discuss.hashicorp.com/t/hcsec-2021-17-consul-s-envoy-tls-configuration-did-not-validate-destination-service-subject-alternative-names/26856
- https://github.com/hashicorp/consul/releases/tag/v1.10.1
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
