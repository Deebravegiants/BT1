# [H] DevSpace UI Server WebSocket CheckOrigin does not validate source

## Summary
Severity: High
Advisory: GHSA-hqwm-7x7x-8379
CVE: CVE-2026-42283
CWE: CWE-200, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-hqwm-7x7x-8379
Type: github-advisory

## Affected
- Go: `github.com/loft-sh/devspace` — affected >=6.3.20 <6.3.21

## Details
### Description

DevSpace's UI server WebSocket accepts connections from all origins by default, and therefore several endpoints are exposed via this WebSocket. When a developer runs the DevSpace UI and at the same time uses a browser to access the internet, a malicious website they visit can use their browser to establish a cross-origin WebSocket connection to `ws://127.0.0.1:8090`. This allows an attacker to access: 
* `/api/logs` to stream real-time pod logs
* `/api/enter` to open an interactive shell inside the running pod
* `/api/command` to execute pre-defined pipeline commands

### Patches

Versions 6.3.21 and above are patched.

### Resources

[gorilla/websocket CheckOrigin documentation](https://pkg.go.dev/github.com/gorilla/websocket#hdr-Origin_Considerations)

### Installation Options

Devspace is no longer publishing to NPM or Yarn, please continue to use our [other installation methods](https://www.devspace.sh/docs/getting-started/installation) to get updates in the future, including this patch.

### Credit

DevSpace thanks @b0b0haha for finding and reporting this vulnerability.

## References
- https://github.com/devspace-sh/devspace/security/advisories/GHSA-hqwm-7x7x-8379
- https://nvd.nist.gov/vuln/detail/CVE-2026-42283
- https://github.com/devspace-sh/devspace
