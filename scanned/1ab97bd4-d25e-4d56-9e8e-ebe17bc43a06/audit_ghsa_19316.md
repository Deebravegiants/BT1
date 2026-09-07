# [M] Inspektor Gadget Security Policies Can be Bypassed

## Summary
Severity: Medium
Advisory: GHSA-pv22-fqcj-7xwh
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-pv22-fqcj-7xwh
Type: github-advisory

## Affected
- Go: `github.com/inspektor-gadget/inspektor-gadget` — affected >=0.31.0 <0.40.0

## Details
Security policies like [`allowed-gadgets`](https://inspektor-gadget.io/docs/latest/reference/restricting-gadgets),  [`disallow-pulling`](https://inspektor-gadget.io/docs/latest/reference/disallow-pulling), [`verify-image`](https://inspektor-gadget.io/docs/latest/reference/verify-assets#verify-image-based-gadgets) can be bypassed by a malicious client.

### Impact

Users running `ig` in daemon mode or IG on Kubernetes that rely on any of the features mentioned above are vulnerable to this issue. In order to exploit this, the client needs access to the server, like the correct TLS certificates on the `ig daemon` case or access to the cluster in the Kubernetes case. 

### Patches

The issue has been fixed in v0.40.0

### Workarounds

There is not known workaround to fix it.

## References
- https://github.com/inspektor-gadget/inspektor-gadget/security/advisories/GHSA-pv22-fqcj-7xwh
- https://github.com/inspektor-gadget/inspektor-gadget/commit/c51d419964f5b6f9344fcad4faba70e2e025212b
- https://github.com/inspektor-gadget/inspektor-gadget
- https://pkg.go.dev/vuln/GO-2025-3665
