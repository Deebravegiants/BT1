# [H] Unauthenticated control plane denial of service attack in Istio

## Summary
Severity: High
Advisory: GHSA-856q-xv3c-7f2f
CVE: CVE-2022-23635
CWE: CWE-1284, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-23
Source: https://github.com/advisories/GHSA-856q-xv3c-7f2f
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=1.13.0 <1.13.1
- Go: `istio.io/istio` — affected >=1.12.0 <1.12.4
- Go: `istio.io/istio` — affected >=0 <1.11.7

## Details
### Impact
The Istio control plane, `istiod`, is vulnerable to a request processing error, allowing a malicious attacker that sends a specially crafted message which results in the control plane crashing. This endpoint is served over TLS port 15012, but does not require any authentication from the attacker.

For simple installations, Istiod is typically only reachable from within the cluster, limiting the blast radius. However, for some deployments, especially [multicluster](https://istio.io/latest/docs/setup/install/multicluster/primary-remote/) topologies, this port is exposed over the public internet.

### Patches

- Istio 1.13.1 and above
- Istio 1.12.4 and above
- Istio 1.11.7 and above

### Workarounds
There are no effective workarounds, beyond upgrading. Limiting network access to Istiod to the minimal set of clients can help lessen the scope of the vulnerability to some extent.

### References
More details can be found in the [Istio Security Bulletin](https://istio.io/latest/news/security/istio-security-2022-003)

### For more information
If you have any questions or comments about this advisory, please email us at [istio-security-vulnerability-reports@googlegroups.com](mailto:istio-security-vulnerability-reports@googlegroups.com)

## References
- https://github.com/istio/istio/security/advisories/GHSA-856q-xv3c-7f2f
- https://nvd.nist.gov/vuln/detail/CVE-2022-23635
- https://github.com/istio/istio/commit/5f3b5ed958ae75156f8656fe7b3794f78e94db84
- https://github.com/istio/istio
- https://istio.io/latest/news/security/istio-security-2022-003
