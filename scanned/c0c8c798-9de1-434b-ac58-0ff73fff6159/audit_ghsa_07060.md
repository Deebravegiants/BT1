# [M] Coder vulnerable to denial of service via unbounded request body in AI Bridge provider endpoints

## Summary
Severity: Medium
Advisory: GHSA-f5vp-w269-392g
CVE: CVE-2026-55434
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-f5vp-w269-392g
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8

## Details
### Summary

AI Bridge provider handlers read request bodies with `io.ReadAll` without a maximum size so an authenticated user with AI Bridge access could send an arbitrarily large body and exhaust memory.

> **Note:** Exploitation requires authenticated access to the AI Bridge endpoints and the impact is limited to availability (denial of service).

### Impact

An authenticated member-level user could POST a very large or chunked body to an AI Bridge provider endpoint such as `/api/v2/aibridge/anthropic/v1/messages`, growing heap memory until the operating system terminates the process. Because AI Bridge runs in-process with `coderd`, this crashes the entire control plane, including the API, workspace coordinator and DERP relay. It requires an authenticated user and the AI Bridge feature enabled.

### Patches

The fix applies `http.MaxBytesReader` or an equivalent cap before reading provider and session request bodies. The affected AI Bridge provider endpoints exist only on the v2.33 and v2.34 lines. Earlier release lines are not affected.

The fix is available in the following releases:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |

### Workarounds

None.

### Resources

- Fix: #26164

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22443) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-f5vp-w269-392g
- https://nvd.nist.gov/vuln/detail/CVE-2026-55434
- https://github.com/coder/coder/pull/26164
- https://github.com/coder/coder
- https://github.com/coder/coder/releases/tag/v2.33.8
- https://github.com/coder/coder/releases/tag/v2.34.2
