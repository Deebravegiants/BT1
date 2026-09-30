# [H] Netmaker vulnerable to Insufficient Granularity of Access Control

## Summary
Severity: High
Advisory: GHSA-ggf6-638m-vqmg
CVE: CVE-2022-36110
CWE: CWE-1220, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-ggf6-638m-vqmg
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <0.15.1

## Details
### Impact
Improper Authorization functions leads to non-privileged users running privileged API calls. If you have added users to your Netmaker platform who whould not have admin privileges, they could use their auth token to run admin-level functions via the API.

In addition, differing response codes based on function calls allowed non-users to potentially brute force the determination of names of networks on the system.

### Patches
This problem has been patched in v0.15.1. To apply:

1. docker-compose down
2. docker pull gravitl/netmaker:v0.15.1
3. docker-compose up -d

### For more information
If you have any questions or comments about this advisory:

Email us at [info@netmaker.io](mailto:info@netmaker.io)
This vulnerability was brought to our attention by @tweidinger

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-ggf6-638m-vqmg
- https://nvd.nist.gov/vuln/detail/CVE-2022-36110
- https://github.com/gravitl/netmaker
- https://github.com/gravitl/netmaker/releases/tag/v0.15.1
