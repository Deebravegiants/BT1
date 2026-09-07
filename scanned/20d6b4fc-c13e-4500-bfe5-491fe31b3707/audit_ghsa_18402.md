# [H] Chall-Manager's HTTP Gateway is vulnerable to DoS due to missing header timeout

## Summary
Severity: High
Advisory: GHSA-ggmv-j932-q89q
CVE: CVE-2025-53634
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-ggmv-j932-q89q
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/chall-manager` — affected >=0 <0.1.4

## Details
### Impact
The HTTP Gateway processes headers, but with no timeout set. With a Slowloris attack, an attacker could cause Denial of Service (DoS).
Exploitation does not require authentication nor authorization, so anyone can exploit it. It should nonetheless not be exploitable as it is highly recommended to bury Chall-Manager deep within the infrastructure due to its large capabilities, so no users could reach the system.

### Patches
Patch has been implemented by [commit `1385bd8`](https://github.com/ctfer-io/chall-manager/commit/1385bd869142651146cd0b123085f91cec698636) and shipped in [`v0.1.4`](https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4).

### Workarounds
No workaround exist.

### References
N/A

## References
- https://github.com/ctfer-io/chall-manager/security/advisories/GHSA-ggmv-j932-q89q
- https://nvd.nist.gov/vuln/detail/CVE-2025-53634
- https://github.com/ctfer-io/chall-manager/commit/1385bd869142651146cd0b123085f91cec698636
- https://github.com/ctfer-io/chall-manager
- https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4
