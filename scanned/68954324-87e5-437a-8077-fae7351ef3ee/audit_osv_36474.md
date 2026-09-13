# [M] CVE-2026-23766

## Summary
Severity: Medium
Advisory: CVE-2026-23766
CVSS: 4.1 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2026-23766
Type: osv

## Details
Istio through 1.28.2 allows iptables rule injection for changing firewall behavior via the traffic.sidecar.istio.io/excludeInterfaces annotation. NOTE: the reporter's position is "this doesn't represent a security vulnerability (pod creators can already exclude sidecar injection entirely)."

## References
- https://github.com/istio/istio/issues/58781
- https://github.com/istio/istio/pull/58785
