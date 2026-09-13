# [M] DOS bitswap unbounded persistant memory leak

## Summary
Severity: Medium
Chain: IPFS
Component: ipfs/kubo
CWE: Uncontrolled Resource Consumption
Published: 2023-05-10
Source: https://github.com/ipfs/kubo/security/advisories/GHSA-qvqg-6rp8-4p9h
Type: github-advisory

## Details
### Impact
An attacker is able allocate arbitrarily many bytes in the Bitswap server by sending many `WANT_BLOCK` and or `WANT_HAVE` requests which are queued in an unbounded queue, with allocations that persist even if the connection is closed.

This affects users accepting or connecting untrusted connections such as by running in the public swarm and no pnet config.
Nodes that are not publicly reachable but connects to untrusted nodes are also vulnerable to the untrusted nodes being connected to since libp2p connections are blindly bidirectional.

### Patches
- 19feb15833c6f4d6e7f1e1b132efaae96d76481d [`boxo`](https://github.com/ipfs/boxo) update in Kubo
- GHSA-m974-xj4j-7qv5 patches in boxo

### Workarounds

Use [PNET](https://github.com/ipfs/kubo/blob/master/docs/experimental-features.md#private-networks), [swarm filters](https://github.com/ipfs/kubo/blob/master/docs/config.md#swarmaddrfilters) or [resource manager allows list](https://pkg.go.dev/github.com/libp2p/go-libp2p/p2p/host/resource-manager#readme-allowlisting-multiaddrs-to-mitigate-eclipse-attacks) to block untrusted connections.

Note that using the resource manager will disrupt both client and server features because the bitswap protocol is a message based protocol mixing requests and responses.

### References
- GHSA-m974-xj4j-7qv5
- [CVE-2023-25568](https://nvd.nist.gov/vuln/detail/CVE-2023-25568)
