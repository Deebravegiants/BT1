# [H] HashiCorp Consul Template could reveal Vault secret contents in error messages

## Summary
Severity: High
Advisory: GHSA-8449-7gc2-pwrp
CVE: CVE-2022-38149
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-8449-7gc2-pwrp
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul-template` — affected >=0 <0.27.3
- Go: `github.com/hashicorp/consul-template` — affected >=0.28.0 <0.28.3
- Go: `github.com/hashicorp/consul-template` — affected >=0.29.0 <0.29.2

## Details
In HashiCorp Consul Template through version 0.29.1, invalid templates could inadvertently reveal the contents of Vault secret in errors returned by the `*template.Template.Execute 5` method, when given a template using Vault secret contents incorrectly. This method has been updated to redact Vault secrets when creating an error string, making it safe to log the error.. This issue was fixed in version 0.29.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38149
- https://github.com/hashicorp/consul-template/commit/d6a6f4af219c28e67d847ba0e0b2bea8f5bb9076
- https://discuss.hashicorp.com/t/hsec-2022-16-consul-template-may-expose-vault-secrets-when-processing-invalid-input/43215
- https://github.com/hashicorp/consul
- https://pkg.go.dev/vuln/GO-2022-0980
