# [M] Kong Ingress Controller for Kubernetes (KIC): Secret-backed plugin configurations leak through non-sensitive diagnostics endpoint

## Summary
Severity: Medium
Advisory: GHSA-3278-c88v-xrh4
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-3278-c88v-xrh4
Type: github-advisory

## Affected
- Go: `github.com/kong/kubernetes-ingress-controller/v3` — affected >=0 <3.5.7
- Go: `github.com/kong/kubernetes-ingress-controller/v2` — affected >=0
- Go: `github.com/kong/kubernetes-ingress-controller` — affected >=0

## Details
## Summary

A vulnerability in the Kong Ingress Controller (KIC) allows for the unauthorized exposure of sensitive plugin credentials through the diagnostics interface. Even when configured to redact sensitive information (using `--dump-sensitive-config=false`), KIC fails to sanitize the `Plugins` field in diagnostic configuration dumps. This causes secrets referenced via `configFrom.secretKeyRef` to be resolved and displayed in plaintext.

Because the diagnostics HTTP endpoints require no authentication, any process within the cluster network capable of reaching the KIC pod can exfiltrate sensitive data, including API keys, bearer tokens, and database passwords.

## Am I affected?

You are affected if all of the following hold:
1. You are using Kong Ingress Controller with **diagnostics enabled** (`--dump-config=true`).
2. You have **not explicitly enabled** sensitive dumping (`--dump-sensitive-config=false`), creating an expectation of redaction.
3. You use `KongPlugin` or `KongClusterPlugin` resources that reference Kubernetes Secrets via **`configFrom.secretKeyRef`**.
4. The KIC diagnostics port (default `10256`) is reachable by other workloads or users within your cluster.

You are not affected if:
- The `--dump-config` flag is set to `false` (default behavior).
- You do not use secret-backed configurations in your Kong plugins.
- Access to the KIC pod's diagnostic port is strictly blocked by NetworkPolicies.

## Mitigation

1. **Disable Diagnostics**: If not actively debugging, disable the diagnostic server by setting `--dump-config=false`.
2. **Network Isolation**: Implement a `NetworkPolicy` to restrict access to the KIC diagnostics port (default `10256`), ensuring only authorized administrative pods or IPs can reach it.
3. **Restrict Port-Forwarding**: Limit `kubectl port-forward` RBAC permissions to prevent unauthorized users from accessing the pod's local ports.

## Fix

The fix introduces proper sanitization for the `Plugins` field within the configuration state. When sensitive dumping is disabled, the controller now replaces all plugin configuration values with a redaction placeholder before they are served via the diagnostics endpoints. Additionally, it is recommended to ensure your deployment environment follows the principle of least privilege regarding network access to controller components.

Users should upgrade to the latest patched version of Kong Ingress Controller to ensure diagnostic dumps are correctly redacted.

## References
- https://github.com/Kong/kubernetes-ingress-controller/security/advisories/GHSA-3278-c88v-xrh4
- https://github.com/Kong/kubernetes-ingress-controller
