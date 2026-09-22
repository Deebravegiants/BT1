# [M] Cilium may not enforce host firewall policies when Native Routing, WireGuard and Node Encryption are enabled

## Summary
Severity: Medium
Advisory: GHSA-5r23-prx4-mqg3
CVE: CVE-2026-26963
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-5r23-prx4-mqg3
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.18.0 <1.18.6

## Details
### Impact

[Host Policies](https://docs.cilium.io/en/stable/security/policy/language/#host-policies) will incorrectly permit traffic from Pods on other nodes when all of the following configurations are enabled:
* [Native Routing](https://docs.cilium.io/en/stable/network/concepts/routing/#native-routing)
* [WireGuard](https://docs.cilium.io/en/stable/security/policy/language/#host-policies)
* [Node Encryption](https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#node-to-node-encryption-beta) (beta)

These options are disabled by default in Cilium.

### Patches

This issue was fixed by #42892.

This issue affects:

* Cilium v1.18 between v1.18.0 and v1.18.5 inclusive

This issue is fixed in:

* Cilium v1.18.6

### Workarounds

There is currently no officially verified or comprehensive workaround for this issue. The following procedure has been validated strictly within a local 'Kind' environment and has not undergone exhaustive testing across diverse production architectures. Proceed with caution.

To mitigate the identified traffic bypass, ensure all ingress traffic from the `cilium_wg0` interface is explicitly routed to `cilium_host` for policy enforcement. This ensures that host-level security policies are applied to decrypted WireGuard traffic. Execute the following configuration on each CiliumNode:

```bash
# IPv4 Traffic
ip rule add iif cilium_wg0 table 300
ip route add default dev cilium_host table 300

# IPv6 Traffic
ip -6 rule add iif cilium_wg0 table 300
ip -6 route add default dev cilium_net table 300
```

### Acknowledgements

Special thanks to @julianwiedmann for reporting the issue and helping with the resolution.

### For more information

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at security@cilium.io. This is a private mailing list for the Cilium security team, and your report will be treated as top priority. Please also address any comments or questions on this advisory to the same mailing list.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-5r23-prx4-mqg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26963
- https://github.com/cilium/cilium/pull/42892
- https://github.com/cilium/cilium/commit/88e28e1e62c0b1a02c3f0fc22d888ac9eefbe885
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.18.6
