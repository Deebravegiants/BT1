# [M] Kubetail has a Cross-Site WebSocket Hijacking issue that allows attacker to read Kubernetes logs from authenticated users

## Summary
Severity: Medium
Advisory: GHSA-v8j7-hp7c-738f
CVE: CVE-2026-44514
CWE: CWE-1385
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-v8j7-hp7c-738f
Type: github-advisory

## Affected
- Go: `github.com/kubetail-org/kubetail/modules/dashboard` — affected >=0 <0.14.0
- Go: `github.com/kubetail-org/kubetail/modules/cli` — affected >=0 <0.16.0

## Details
### Summary

Kubetail's dashboard exposes WebSocket endpoints that did not adequately validate the Origin header on connection upgrade. A malicious web page visited by a user with an active Kubetail session could open a WebSocket to the user's dashboard and read their Kubernetes logs in real time. This is a Cross-Site WebSocket Hijacking (CSWSH) vulnerability and affects both the desktop deployment (default http://localhost:7500) and cluster deployments (typically behind an Ingress with HTTP basic auth).

### Impact

An attacker who can convince an authenticated Kubetail user to visit a page they control can:

- Establish a WebSocket connection to the victim's dashboard from the attacker's origin
- Stream container logs the victim has access to via the Kubernetes API
- Exfiltrate the contents to an attacker-controlled server

The attacker gains **read-only** access to logs — no write or destructive operations are exposed. However, container logs frequently contain credentials accidentally written by application code, bearer tokens, internal hostnames, customer PII, and other secrets, so the practical impact of read access can be significant.

The desktop deployment is particularly exposed because the dashboard is reachable at a predictable localhost URL, requires no network reachability from the attacker, and the browser will attach ambient credentials to the WebSocket handshake.
For cluster deployments fronted by HTTP basic auth, the browser's automatic re-sending of basic-auth credentials on the WebSocket upgrade request enables the same attack against the configured dashboard origin.

### Affected versions

| Component                                    | Name                           | Affected | Patched   |
| --------------------------------- | ---------------------- | -------- | ---------- |
| Kubetail Dashboard docker image | `kubetail-dashboard` | < 0.14.0  | >= 0.14.0  |
| Kubetail Helm Chart                       | `kubetail/kubetail`       | < 0.23.0 | >= 0.23.0 |
| Kubetail CLI                                    | `kubetail`                     | < 0.16.0 | >= 0.16.0  |

Confirmed in Google Chrome. Microsoft Edge is presumed affected as it shares Chromium's WebSocket implementation, but was not directly tested.

**Preconditions for exploitation**

1. The victim has an active authenticated Kubetail session (desktop dashboard running, or browser holding valid credentials for a cluster deployment).
2. The victim visits a web page controlled by the attacker in the same browser.
3. The attacker knows or can guess the dashboard URL (trivial for desktop; cluster deployments require knowing the Ingress hostname).

### Patches

Upgrade to:
* Kubetail Dashboard 0.14.0 or later
* Kubetail Helm Chart 0.23.0 or later
* Kubetail CLI 0.16.0 or later

### Workarounds

If users cannot upgrade immediately:

* **Desktop:** Stop the dashboard (kubetail CLI process) when not actively in use. Avoid visiting untrusted sites in the same browser profile while the dashboard is running.
* **Cluster:** Restrict Ingress access to a VPN, bastion, or office network. Add a stronger outer authentication layer (e.g. OAuth proxy) in front of basic auth. Consider browser profile isolation for cluster admins.

## References
- https://github.com/kubetail-org/kubetail/security/advisories/GHSA-v8j7-hp7c-738f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44514
- https://github.com/kubetail-org/kubetail
