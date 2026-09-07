# [H] Cloudflare GoFlow vulnerable to a Denial of Service in the sflow packet handling package

## Summary
Severity: High
Advisory: GHSA-9rpw-2h95-666c
CVE: CVE-2022-2529
CWE: CWE-20, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-9rpw-2h95-666c
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/goflow/v3` — affected >=0 <3.4.4

## Details
### Impact
The sflow decode package prior to version 3.4.4 does not employ sufficient packet sanitisation which can lead to a denial of service attack. Attackers can craft malformed packets causing the process to consume huge amounts of memory resulting in a denial of service.

### Specific Go Packages Affected
github.com/cloudflare/goflow/v3/decoders/sflow

### Patches
Version 3.4.4 contains patches fixing this.

### Workarounds
A possible workaround is to not have your goflow collector publicly reachable.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [goflow repo](https://github.com/cloudflare/goflow)
* Email us [netdev[@]cloudflare.com ](mailto:netdev@cloudflare.com)

## References
- https://github.com/cloudflare/goflow/security/advisories/GHSA-9rpw-2h95-666c
- https://nvd.nist.gov/vuln/detail/CVE-2022-2529
- https://github.com/cloudflare/goflow/commit/2b94619a6204443e3ca1769f4e459f9f57039c51
- https://github.com/cloudflare/goflow/commit/c829ccd2c0aafdc9b886b20bf6f28095607f4998
- https://github.com/cloudflare/goflow
- https://github.com/cloudflare/goflow/releases/tag/v3.4.4
