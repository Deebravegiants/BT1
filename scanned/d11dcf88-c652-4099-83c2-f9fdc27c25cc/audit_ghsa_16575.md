# [M] sshpiper's enabling of proxy protocol without proper feature flagging allows faking source address

## Summary
Severity: Medium
Advisory: GHSA-4w53-6jvp-gg52
CVE: CVE-2024-35175
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-4w53-6jvp-gg52
Type: github-advisory

## Affected
- Go: `github.com/tg123/sshpiper` — affected >=1.0.50 <1.3.0

## Details
### Summary

The way the proxy protocol listener is implemented in sshpiper can allow an attacker to forge their connecting address.

### Details

[This commit](https://github.com/tg123/sshpiper/commit/2ddd69876a1e1119059debc59fe869cb4e754430) added the proxy protocol listener as the only listener in sshpiper, with no option to toggle this functionality off. This means that any connection that sshpiper is directly (or in some cases indirectly) exposed to can use proxy protocol to forge its source address.

### PoC

You can use a configuration like this in HAProxy:

```
listen w-send-proxy
    mode tcp
    log global
    option tcplog
    bind *:27654
    tcp-request connection set-src ipv4(1.1.1.1)
    server app1 ssh-piper-hostname:22 send-proxy
```

When connecting through HAProxy, sshpiper will log connections as originating from `1.1.1.1`.  The proxy protocol data is designed to survive multiple load balancers or proxies and pass through to sshpiper at the end, so it should only be enabled trusted environments. This should be behind a configuration option or startup flag to prevent abuse when public connections can be made to sshpiper.

This is also backed up by [the specification for proxy protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt):

> The receiver MUST be configured to only receive the protocol described in this
specification and MUST not try to guess whether the protocol header is present
or not. This means that the protocol explicitly prevents port sharing between
public and private access. Otherwise it would open a major security breach by
allowing untrusted parties to spoof their connection addresses. The receiver
SHOULD ensure proper access filtering so that only trusted proxies are allowed
to use this protocol.

### Impact

Any users of sshpiper who need logs from it for whitelisting/rate limiting/security investigations could have them become much less useful if an attacker is sending a spoofed source address.

## References
- https://github.com/tg123/sshpiper/security/advisories/GHSA-4w53-6jvp-gg52
- https://nvd.nist.gov/vuln/detail/CVE-2024-35175
- https://github.com/tg123/sshpiper/commit/2ddd69876a1e1119059debc59fe869cb4e754430
- https://github.com/tg123/sshpiper/commit/70fb830dca26bea7ced772ce5d834a3e88ae7f53
- https://github.com/tg123/sshpiper
