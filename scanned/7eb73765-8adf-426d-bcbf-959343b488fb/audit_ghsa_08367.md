# [M] Ironic Standalone Operator's prometheus metrics exporter bound to all interfaces

## Summary
Severity: Medium
Advisory: GHSA-7cwm-fpfh-rrch
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-7cwm-fpfh-rrch
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/ironic-standalone-operator` — affected >=0 <0.9.0

## Details
## Impact

The Ironic Standalone Operator (IRSO) is the operator to maintain an Ironic deployment for Metal3. The Prometheus metrics exporter binds to 0.0.0.0 (all network interfaces) by default with no authentication. The default config is disabled. If enabled, this exposes operational metrics to any host on adjacent networks. Deployments running IrSO v0.7.0 through v0.8.1 with the Prometheus exporter enabled are affected. Versions prior to v0.7.0 do not have the Prometheus exporter feature.

## Patches

The exporter now exposes a configurable bindAddress field. Users should upgrade to v0.9.0 or later. 

## Workarounds

Users on older versions than v0.9.0 should use host-level firewall rules (iptables/nftables) to restrict access to the metrics port from unintended networks, or disable the metrics service.

## Resources

- https://github.com/metal3-io/ironic-standalone-operator/pull/635

## References
- https://github.com/metal3-io/ironic-standalone-operator/security/advisories/GHSA-7cwm-fpfh-rrch
- https://github.com/metal3-io/ironic-standalone-operator/pull/635
- https://github.com/metal3-io/ironic-standalone-operator
