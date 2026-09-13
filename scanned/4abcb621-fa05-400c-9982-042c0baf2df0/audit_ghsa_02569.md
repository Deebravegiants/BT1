# [H] OctoRPKI lacks contextual out-of-bounds check when validating RPKI ROA maxLength values

## Summary
Severity: High
Advisory: GHSA-c8xp-8mf3-62h9
CVE: CVE-2021-3761
CWE: CWE-295, CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-c8xp-8mf3-62h9
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.3.0

## Details
Any CA issuer in the RPKI can trick OctoRPKI prior to https://github.com/cloudflare/cfrpki/commit/a8db4e009ef217484598ba1fd1c595b54e0f6422 into emitting an invalid VRP "MaxLength" value, causing RTR sessions to terminate. 

### Impact

An attacker can use this to disable RPKI Origin Validation in a victim network (for example AS 13335 - Cloudflare) prior to launching a BGP hijack which during normal operations would be rejected as "RPKI invalid". Additionally, in certain deployments RTR session flapping in and of itself also could cause BGP routing churn, causing availability issues.

### Patches
https://github.com/cloudflare/cfrpki/commit/a8db4e009ef217484598ba1fd1c595b54e0f6422

https://github.com/cloudflare/cfrpki/releases/tag/v1.3.0

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@cloudflare.com](security@cloudflare.com)

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-c8xp-8mf3-62h9
- https://nvd.nist.gov/vuln/detail/CVE-2021-3761
- https://github.com/cloudflare/cfrpki/pull/90
- https://github.com/cloudflare/cfrpki/commit/a8db4e009ef217484598ba1fd1c595b54e0f6422
- https://github.com/cloudflare/cfrpki/releases/tag/v1.3.0
- https://pkg.go.dev/vuln/GO-2022-0246
- https://www.debian.org/security/2022/dsa-5041
- github.com/cloudflare/cfrpki
