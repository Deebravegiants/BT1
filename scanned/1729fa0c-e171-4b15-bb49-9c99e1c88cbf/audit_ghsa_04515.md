# [H] OpenTelemetry Operator for Kubernetes's ServiceMonitor bearerTokenFile reads arbitrary local file and sends contents as bearer auth

## Summary
Severity: High
Advisory: GHSA-cxh2-4639-vmc5
CVE: CVE-2026-47701
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-cxh2-4639-vmc5
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-operator` — affected >=0 <0.152.0

## Details
## Affected

Repository: github.com/open-telemetry/opentelemetry-operator
Component: cmd/otel-allocator (TargetAllocator)
Companion: Prometheus Operator API types (CRDs)

## Summary

OpenTelemetry Operator's TargetAllocator watches `ServiceMonitor` resources via the Prometheus Operator CR watcher and converts each selected endpoint into a Prometheus scrape configuration entry. The endpoint field `bearerTokenFile` is preserved through the conversion as `HTTPClientConfig.Authorization.CredentialsFile`. The OpenTelemetry Collector, configured with the Prometheus receiver, then loads that scrape config and, at scrape time, reads the file from its own pod filesystem and sends the contents as `Authorization: Bearer ...` to the scrape endpoint.

A tenant who can create or update a `ServiceMonitor` selected by TargetAllocator can set `bearerTokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token` and a scrape target the tenant controls. The Collector then ships its mounted service account JWT to that target on every scrape interval.

The Prometheus Operator project addressed the same primitive via the `ArbitraryFSAccessThroughSMs.Deny` admission/runtime guard.

## Preconditions

The OpenTelemetry Collector needs to be deployed with `targetAllocator.prometheusCR.enabled: true` and `serviceMonitorSelector` / `serviceMonitorNamespaceSelector` matching at least one namespace where the attacker can create or update `ServiceMonitor` (or paired with a TargetAllocator resource with the same respective settings). The Collector pod needs to have its service account token mounted. The Collector needs to be able to reach the scrape target chosen by the attacker.

## Impact

Tenant `ServiceMonitor` write becomes equivalent to the OpenTelemetry Collector pod's service account against the Kubernetes API. Real impact depends on what the Collector service account is granted in a given deployment. Typical cluster monitoring setups grant pod, node, endpoint, namespace, and service list across the cluster, which is enough to enumerate and identify further targets. The same primitive can read any file the Collector pod has on disk including mounted certificates and other tokens.

## Fix

https://github.com/open-telemetry/opentelemetry-operator/pull/5104 adds support to disable service and podmonitor endpoints that read arbitrary files. 
`DenyFSAccessThroughSMs` causes the Target Allocator to drop ServiceMonitor and PodMonitor endpoints that reference arbitrary files on the file system. When enabled, endpoints with bearerTokenFile, tlsConfig.caFile, tlsConfig.certFile, or tlsConfig.keyFile are dropped from the produced scrape configuration while the remaining endpoints are kept. This prevents tenants from stealing the Collector's service account token via ServiceMonitor bearerTokenFile references. This is the equivalent of `ArbitraryFSAccessThroughSMs.Deny` from the Prometheus Operator.

## References
- https://github.com/open-telemetry/opentelemetry-operator/security/advisories/GHSA-cxh2-4639-vmc5
- https://github.com/open-telemetry/opentelemetry-operator/pull/5104
- https://github.com/open-telemetry/opentelemetry-operator
