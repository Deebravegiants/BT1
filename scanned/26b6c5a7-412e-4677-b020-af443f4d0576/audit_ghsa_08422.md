# [M] axonflow-sdk-go: Webhook signing-key (HMAC-SHA256) not exposed by SDK type, preventing signature verification

## Summary
Severity: Medium
Advisory: GHSA-mhc4-qq83-fmrr
CWE: CWE-345, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-mhc4-qq83-fmrr
Type: github-advisory

## Affected
- Go: `github.com/getaxonflow/axonflow-sdk-go/v5` — affected >=0 <5.7.0

## Details
## Summary

The AxonFlow SDK's `WebhookSubscription` (or equivalent) type did not expose the HMAC-SHA256 signing key returned by the platform's `CreateWebhook` endpoint. Without access to the secret through the typed SDK API, callers had no path to verify the `X-AxonFlow-Signature` header on incoming webhook deliveries. Affected callers had two unsatisfactory options:

1. Skip signature verification entirely — accepting any payload from any source that knew the webhook URL.
2. Hand-parse the raw HTTP JSON response to extract the secret, bypassing the type-safe SDK surface.

This advisory is filed across all four AxonFlow SDKs (Go, Python, TypeScript, Java) because the same defect and the same fix landed in each.

## Affected versions

Versions 5.6.1 and below.

## Impact

A webhook receiver using the SDK's typed API to handle inbound deliveries had no path to authenticate the source of incoming payloads. An attacker who learned the webhook URL — through misconfiguration, log leakage, observable network traffic during setup, or any other discovery channel — could forge webhook deliveries indistinguishable from legitimate ones, causing the receiving application to act on fabricated events (e.g. simulated approval-granted callbacks, simulated policy-decision callbacks, simulated step-completion callbacks).

## Remediation

Upgrade to the patched version listed in Vulnerabilities below. The signing key is now exposed on the `WebhookSubscription` response type returned by `CreateWebhook`. Implementations should:

1. Persist the secret returned by `CreateWebhook` securely (it is only returned once, at create time).
2. On each incoming webhook delivery, compute `HMAC-SHA256(secret, raw_body)` and compare it in constant time against the `X-AxonFlow-Signature` header.
3. Reject any delivery whose signature does not match.

## Credit

Identified by AxonFlow internal security review during the April 2026 quality-freeze epic.

## References
- https://github.com/getaxonflow/axonflow-sdk-go/security/advisories/GHSA-mhc4-qq83-fmrr
- https://github.com/getaxonflow/axonflow-sdk-go
