# [H] CoreDNS Vulnerable to DoQ Memory Exhaustion via Stream Amplification

## Summary
Severity: High
Advisory: GHSA-cvx7-x8pj-x2gw
CVE: CVE-2025-47950
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-06
Source: https://github.com/advisories/GHSA-cvx7-x8pj-x2gw
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.12.2

## Details
### Summary

A **Denial of Service (DoS)** vulnerability was discovered in the CoreDNS DNS-over-QUIC (DoQ) server implementation. The server previously created a new goroutine for every incoming QUIC stream without imposing any limits on the number of concurrent streams or goroutines. A remote, unauthenticated attacker could open a large number of streams, leading to uncontrolled memory consumption and eventually causing an Out Of Memory (OOM) crash — especially in containerized or memory-constrained environments.

### Impact

- **Component**: `server_quic.go`
- **Attack Vector**: Remote, network-based
- **Attack Complexity**: Low
- **Privileges Required**: None
- **User Interaction**: None
- **Impact**: High availability loss (OOM kill or unresponsiveness)

This issue affects deployments with `quic://` enabled in the Corefile. A single attacker can cause the CoreDNS instance to become unresponsive using minimal bandwidth and CPU.

### Patches

The patch introduces two key mitigation mechanisms:

- **`max_streams`**: Caps the number of concurrent QUIC streams per connection. Default: `256`.
- **`worker_pool_size`**: Introduces a server-wide, bounded worker pool to process incoming streams. Default: `1024`.

This eliminates the 1:1 stream-to-goroutine model and ensures that CoreDNS remains resilient under high concurrency. The new configuration options are exposed through the `quic` Corefile block:

```
quic {
    max_streams 256
    worker_pool_size 1024
}
```

These defaults are generous and aligned with typical DNS-over-QUIC client behavior.

### Workarounds

If you're unable to upgrade immediately, you can:
- Disable QUIC support by removing or commenting out the `quic://` block in your Corefile
- Use container runtime resource limits to detect and isolate excessive memory usage
- Monitor QUIC connection patterns and alert on anomalies

### References

- [RFC 9250 - DNS over Dedicated QUIC Connections](https://datatracker.ietf.org/doc/html/rfc9250)
- [quic-go GitHub project](https://github.com/quic-go/quic-go)
- [QUIC stream exhaustion class of vulnerabilities (related)](https://www.usenix.org/conference/usenixsecurity23/presentation/botella)

### Credit

Thanks to [@thevilledev](https://github.com/thevilledev) for disclovering this vulnerability and contributing a high-quality fix.

### For more information

Please consult our [security guide](https://github.com/coredns/coredns/blob/master/.github/SECURITY.md) for more information regarding our security process.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-cvx7-x8pj-x2gw
- https://nvd.nist.gov/vuln/detail/CVE-2025-47950
- https://github.com/coredns/coredns/commit/efaed02c6a480ec147b1f799aab7cf815b17dfe1
- https://datatracker.ietf.org/doc/html/rfc9250
- https://github.com/coredns/coredns
- https://github.com/quic-go/quic-go
- https://www.usenix.org/conference/usenixsecurity23/presentation/botella
