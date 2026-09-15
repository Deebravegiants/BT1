# [H] DragonFly's manager generates mTLS certificates for arbitrary IP addresses

## Summary
Severity: High
Advisory: GHSA-255v-qv84-29p5
CVE: CVE-2025-59353
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-255v-qv84-29p5
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
A peer can obtain a valid TLS certificate for arbitrary IP addresses, effectively rendering the mTLS authentication useless. The issue is that the Manager’s Certificate gRPC service does not validate if the requested IP addresses “belong to” the peer requesting the certificate—that is, if the peer connects from the same IP address as the one provided in the certificate request.

```golang
if addr, ok := p.Addr.(*net.TCPAddr); ok {
       ip = addr.IP.String()
} else {
       ip, _, err = net.SplitHostPort(p.Addr.String())
       if err != nil {
             return nil, err
       }
}
// Parse csr.
[skipped]
// Check csr signature.
// TODO check csr common name and so on.
if err = csr.CheckSignature(); err != nil {
       return nil, err
}
[skipped]
// TODO only valid for peer ip
// BTW we need support both of ipv4 and ipv6.
ips := csr.IPAddresses
if len(ips) == 0 {
       // Add default connected ip.
       ips = []net.IP{net.ParseIP(ip)}
}
```
### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-255v-qv84-29p5
- https://nvd.nist.gov/vuln/detail/CVE-2025-59353
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3969
