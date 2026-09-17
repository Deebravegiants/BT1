# [H] Consul-template vulnerable to an information disclosure issue in error handling

## Summary
Severity: High
Advisory: CVE-2026-87993
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-87993
Type: osv

## Details
The consul-template library is vulnerable to an information disclosure issue in its error handling path that may allow Vault secret values to appear in template error messages, log output, and downstream surfaces such as Nomad task events. This vulnerability (CVE-2026-87993) is fixed in consul-template 0.43.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-38-consul-template-vulnerable-to-an-information-disclosure-issue-in-error-handling/77740
- https://github.com/hashicorp/consul-template/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87993.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87993
