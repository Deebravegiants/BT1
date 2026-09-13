# [H] New API: Unauthenticated payment webhooks allow memory and disk DoS via unbounded body reads and full-body logging

## Summary
Severity: High
Advisory: GHSA-v828-m3pf-vq9q
CVE: CVE-2026-64868
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-v828-m3pf-vq9q
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <1.0.0-rc.11

## Details
## Summary

Unauthenticated payment webhook endpoints could read and log the entire request body before validating the webhook signature. When a payment webhook was enabled, an unauthenticated attacker could send oversized requests to public callback endpoints and force excessive memory use and log growth before the request was rejected.

Affected public endpoints included:

- `POST /api/stripe/webhook`
- `POST /api/creem/webhook`
- `POST /api/waffo/webhook`

This issue did not allow forging successful payments, because signature validation still guarded the payment processing logic. The vulnerable behavior was the expensive unauthenticated request processing that occurred before signature validation.

## Impact

A remote unauthenticated attacker could cause denial of service through memory pressure, container OOM/restarts, or disk consumption from full-body logging. The impact is availability-only and is rated High.

## Affected versions

Versions before `v1.0.0-rc.11` are affected. The earlier affected range of `<= v1.0.0-rc.7` was incomplete; the anonymous request body limit was introduced later and first appears in `v1.0.0-rc.11`.

## Patches

This issue is fixed in `v1.0.0-rc.11`. The fix adds `middleware.AnonymousRequestBodyLimit()` and applies it to unauthenticated POST routes, including the payment webhook callbacks. The default limit is controlled by `ANONYMOUS_REQUEST_BODY_LIMIT_KB` and defaults to 512 KiB.

## Workarounds

If upgrading immediately is not possible, operators should disable unused payment webhooks, enforce request body limits at a reverse proxy or load balancer, and ensure application and container logs have rotation and quotas. These mitigations reduce exposure but do not replace upgrading.

## References

- Fixed by commit `d2f7f9ee3adf3ef66798783a60d7bc712451c85c`.
- Relevant code paths: `router/api-router.go`, `middleware/request_body_limit.go`, `controller/topup_stripe.go`, `controller/topup_creem.go`, and `controller/topup_waffo.go`.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-v828-m3pf-vq9q
- https://github.com/QuantumNous/new-api/pull/5244
- https://github.com/QuantumNous/new-api/commit/d2f7f9ee3adf3ef66798783a60d7bc712451c85c
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.11
