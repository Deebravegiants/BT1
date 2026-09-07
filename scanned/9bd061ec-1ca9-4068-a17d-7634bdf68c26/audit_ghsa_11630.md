# [H] Salvo has a Path Traversal in salvo-proxy::encode_url_path allows API Gateway Bypass

## Summary
Severity: High
Advisory: GHSA-f842-phm9-p4v4
CVE: CVE-2026-33242
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-f842-phm9-p4v4
Type: github-advisory

## Affected
- crates.io: `salvo` — affected >=0.39.0 <0.89.3

## Details
### Details

A Path Traversal and Access Control Bypass vulnerability was discovered in the salvo-proxy component of the Salvo Rust framework (v0.89.2). The vulnerability allows an unauthenticated external attacker to bypass proxy routing constraints and access unintended backend paths (e.g., protected endpoints or administrative dashboards). This issue stems from the encode_url_path function, which fails to normalize "../" sequences and inadvertently forwards them verbatim to the upstream server by not re-encoding the "." character.

---

### Technical Details

If someone tries to attack by sending a special code like `%2e%2e`, Salvo changes it back to `../` when it first checks the path. The proxy then gets this plain `../` value. When making the new URL to send forward, the `encode_url_path` function tries to change the path again, but its normal settings do not include the `.` (dot) character. Because of this, the proxy puts `../` straight into the new URL and sends a request like `GET /api/../admin HTTP/1.1` to the backend server.

```rust
// crates/proxy/src/lib.rs (Lines 100-105)

pub(crate) fn encode_url_path(path: &str) -> String {
    path.split('/')
        .map(|s| utf8_percent_encode(s, PATH_ENCODE_SET).to_string())
        .collect::<Vec<_>>()
        .join("/")
}
```

---

### PoC

1 - Setup an Nginx Backend Server for example
2 - Start Salvo Proxy Gateway in other port routing to /api/
3 - Run the curl to test the bypass:

```bash
curl -s http://127.0.0.1:8080/gateway/api/%2e%2e%2fadmin/index.html
```

---

### Impact

If attackers take advantage of this problem, they can get past API Gateway security checks and route limits without logging in. This could accidentally make internal services, admin pages, or folders visible.

The attack works because the special path is sent as-is to the backend, which often happens in systems that follow standard web address rules. Attackers might also use different ways of writing URLs or add extra parts to the web address to get past simple security checks that only look for exact `../` patterns.

---

### Remediation

Instead of changing the text of the path manually, the proxy should use a standard way to clean up the path according to RFC 3986 before adding it to the main URL. It is better to use a trusted tool like the URL crate to join paths, or to block any path parts with “..” after decoding them. But a custom implementation maybe looks like:

```rust
pub(crate) fn encode_url_path(path: &str) -> String {
    let normalized = normalize_path(path);
    normalized.split('/')
        .map(|s| utf8_percent_encode(s, PATH_ENCODE_SET).to_string())
        .collect::<Vec<_>>()
        .join("/")
}

fn normalize_path(path: &str) -> String {
    let mut stack = Vec::new();
    for part in path.split('/') {
        match part {
            "" | "." => (), 
            ".." => { let _ = stack.pop(); },
            _ => stack.push(part),
        }
    }
    stack.join("/")
}
```
---

**Vulnerable code introduced in:**
https://github.com/salvo-rs/salvo/commit/7bac30e6960355c58e358e402072d4a3e5c4e1bb#diff-e319bf7afcb577f7e9f4fb767005072f6335d23f306dd52e8c94f3d222610d02R20

---

**Author**: Tomas Illuminati

## References
- https://github.com/salvo-rs/salvo/security/advisories/GHSA-f842-phm9-p4v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33242
- https://github.com/salvo-rs/salvo/commit/7bac30e6960355c58e358e402072d4a3e5c4e1bb#diff-e319bf7afcb577f7e9f4fb767005072f6335d23f306dd52e8c94f3d222610d02R20
- https://github.com/salvo-rs/salvo
- https://github.com/salvo-rs/salvo/releases/tag/v0.89.3
