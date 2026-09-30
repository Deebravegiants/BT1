# [M] opentelemetry_sdk has unbounded memory allocation in W3C Baggage propagation

## Summary
Severity: Medium
Advisory: GHSA-w9wp-h8wv-79jx
CVE: CVE-2026-48504
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-w9wp-h8wv-79jx
Type: github-advisory

## Affected
- crates.io: `opentelemetry_sdk` — affected >=0 <0.32.1

## Details
## Summary

`BaggagePropagator::extract_with_context` in `opentelemetry_sdk` did not enforce the W3C Baggage size limits before parsing an inbound `baggage` header. A large attacker-controlled header could cause unnecessary CPU work and short-lived heap allocations while parsing entries that would later be discarded by the SDK's baggage storage limits.

The SDK now applies limits aligned with the W3C Baggage limits:

  - 64 list-members
  - 8192 bytes total

## Impact

Services that accept untrusted inbound propagation headers may experience increased per-request resource usage when processing oversized `baggage` headers. This can contribute to denial-of-service risk, especially when application or transport-level header limits are absent or configured above the W3C Baggage limits.
 
The impact is limited to availability. This issue does not expose telemetry data, modify telemetry data, or allow code execution.

## Patches

Upgrade `opentelemetry_sdk` to version `0.32.1` or later.

Version `0.32.1` rejects `baggage` header values larger than 8192 bytes and limits extraction to the first 64 list-members.

  ## Workarounds

If upgrading immediately is not possible, reject or limit inbound `baggage` headers larger than 8192 bytes before invoking OpenTelemetry propagation extraction. This can be enforced at a proxy, gateway, middleware layer, or custom carrier boundary.

## Resources

  - W3C Baggage limits: https://www.w3.org/TR/baggage/#limits
  - Related OpenTelemetry Java advisory: https://github.com/open-telemetry/opentelemetry-java/security/advisories/GHSA-rcgg-9c38-7xpx
  - Related OpenTelemetry Go advisory: https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-mh2q-q3fh-2475
  - CVE-2026-48504

## Credit

tonghuaroot

## References
- https://github.com/open-telemetry/opentelemetry-rust/security/advisories/GHSA-w9wp-h8wv-79jx
- https://github.com/open-telemetry/opentelemetry-rust
