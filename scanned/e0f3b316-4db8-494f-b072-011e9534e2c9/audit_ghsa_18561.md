# [H] Chall-Manager's scenario decoding process does not check for zip bombs

## Summary
Severity: High
Advisory: GHSA-r7fm-3pqm-ww5w
CVE: CVE-2025-53633
CWE: CWE-405, CWE-409
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-r7fm-3pqm-ww5w
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/chall-manager` — affected >=0 <0.1.4

## Details
### Impact

When decoding a scenario (i.e. a zip archive), the size of the decoded content is not checked, potentially leading to zip bombs decompression.
Exploitation does not require authentication nor authorization, so anyone can exploit it. It should nonetheless not be exploitable as it is highly recommended to bury Chall-Manager deep within the infrastructure due to its large capabilities, so no users could reach the system.

### Patches

Patch has been implemented by [commit `14042aa`](https://github.com/ctfer-io/chall-manager/commit/14042aa66a577caee777e10fe09adcf2587d20dd) and shipped in [`v0.1.4`](https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4).

### Workarounds

No workaround exist.

### References

N/A.

## References
- https://github.com/ctfer-io/chall-manager/security/advisories/GHSA-r7fm-3pqm-ww5w
- https://nvd.nist.gov/vuln/detail/CVE-2025-53633
- https://github.com/ctfer-io/chall-manager/commit/14042aa66a577caee777e10fe09adcf2587d20dd
- https://github.com/ctfer-io/chall-manager
- https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4
