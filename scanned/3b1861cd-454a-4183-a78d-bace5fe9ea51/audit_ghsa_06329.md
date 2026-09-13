# [C] New API: Integer overflow in quota billing yields negative charges (self-crediting)

## Summary
Severity: Critical
Advisory: GHSA-8r8v-xf7q-rcpr
CVE: CVE-2026-71479
CWE: CWE-190, CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-8r8v-xf7q-rcpr
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <1.0.0-rc.18

## Details
## Summary

Multiple billing paths multiplied **user-controlled quantity parameters** into the quota calculation without an upper bound or overflow-safe integer conversion. A crafted extreme value (e.g. image `n = 18446744073686646784`, a wrapped-negative accepted by a `*uint` field) makes conversions like `int(float64(quota) * n)` wrap past the int64/int32 range into a large **negative** quota. The negative quota takes effect at **settlement** (not at pre-consume), where it is equivalent to crediting the user's balance — turning a small positive balance into an enormous one.

## Timeline（UTC+8）

This vulnerability was confirmed **exploited in the wild**. Response timeline (UTC+8):

- **2026-07-06 23:00** — Community user @lihui12388 reported that their deployment had been exploited via this vulnerability (large negative consumption entries in logs and abnormally inflated balances). We confirmed in-the-wild exploitation and started an emergency response immediately.
- **2026-07-07 01:17** — Emergency fix released as [`v1.0.0-rc.18`](https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.18), roughly 2 hours after the report.
- **2026-07-07 (next day)** — Given the confirmed active exploitation, we publicly disclosed the vulnerability and the fixed version to the community the following day so that all operators could upgrade and audit promptly.
- **2026-07-07 13:19** — [`v1.0.0-rc.19`](https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.19) released with additional observability (quota-saturation warning logs) to help operators audit and monitor abuse.

## Preconditions

This is **not** a zero-balance freebie. The attacker must hold an account whose wallet balance is `> 0` and at least covers the request's normal (un-inflated) pre-consume amount — the pre-consume gate rejects `userQuota <= 0` and insufficient balance with HTTP 403. Quantity multipliers (`n`, duration, ...) are not applied at pre-consume; the overflow only manifests at settlement, flipping the charge negative and crediting the balance.

**Severity escalates** when the deployment enables any feature that grants free starting balance, because the required positive balance is then obtained at zero cost and at scale: check-in rewards (`CheckinSetting.Enabled`), invite rebates (`QuotaForInviter` / `QuotaForInvitee`), or new-user quota gifts (`QuotaForNewUser`). With self-registration on by default and any of these enabled, an attacker can register (or mass-register) to obtain seed balance for free, then inflate it via a single crafted request — effectively unauthenticated exploitation.

## Impact

A low-privilege user with a positive balance can massively inflate their own balance with a single crafted request (negative settlement = credit), violating billing integrity. Sustained abuse can drain the operator's prepaid upstream funds and render billing/service unavailable. **Exploitation in the wild has been confirmed** (see Timeline above).

## Root cause

Single root cause: user-controlled multipliers lacked upper-bound validation before entering quota math, and the float/decimal-to-int conversions lacked saturation. Because `*uint` accepts huge positive values (a wrapped negative), a `>= 0` check is insufficient — an explicit upper bound is required.

## Fix

Fixed via defense-in-depth: (1) upper-bound validation at request ingress (400 on violation), (2) local clamping of the same quantities on validation-bypass paths (passthrough/metadata/multipart), and (3) centralized saturating conversions in `common/quota_math.go` that clamp to int32 and never wrap. Saturation events are additionally audited on the related consume/task log under `admin_info.quota_saturation` (admin-only) and via request-correlated backend warnings.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-8r8v-xf7q-rcpr
- https://github.com/QuantumNous/new-api/commit/c9943d37ad93477dd937fc4901cc3c4e0fd8aaab
- https://github.com/QuantumNous/new-api/commit/d0bd8aac742d1e160a5ca61743fe35f4fff880e8
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.18
