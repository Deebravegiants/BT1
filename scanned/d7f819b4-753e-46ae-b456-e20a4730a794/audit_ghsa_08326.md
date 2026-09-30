# [H] aiosend: Deserialization of request body before signature verification (Pre-auth DoS) in webhook handler

## Summary
Severity: High
Advisory: GHSA-7m8f-hgjq-8gc9
CVE: CVE-2026-70646
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-7m8f-hgjq-8gc9
Type: github-advisory

## Affected
- PyPI: `aiosend` — affected >=0 <3.0.7

## Details
## Summary

`WebhookHandler.feed_update()` deserializes the entire request body before verifying the HMAC signature. This allows an unauthenticated attacker to force expensive parsing of arbitrary JSON payloads that will ultimately be rejected, leading to unnecessary CPU and memory consumption.

## Severity

**High** (CVSS 7.5)

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
```

## Affected Package

- Ecosystem: PyPI
- Package: `aiosend`

## Affected Versions

- `< 3.0.6`

## Patched Versions

- `>= 3.0.6`

## Details

In `aiosend/webhook/base.py`, `WebhookHandler.feed_update()` performs full Pydantic deserialization before validating the webhook signature:

```python
update = Update.model_validate(body, context={"client": self})
if not self._check_signature(body, headers):
    return False
```

Because authentication occurs only after parsing, anyone can send arbitrarily large JSON payloads with an invalid signature. Although the request is rejected, the server still performs all parsing work.

Additionally, `CryptoPayObject` is configured with:

```python
ConfigDict(extra="allow")
```

allowing arbitrary extra fields to be retained in memory, increasing resource consumption.

## Impact

An unauthenticated attacker can repeatedly send large invalid webhook requests, forcing the server to consume CPU time and memory before rejecting them.

This results in a pre-authentication denial-of-service condition affecting all webhook integrations.

## Affected Components

- `aiosend/webhook/base.py`
- `aiosend/types/base.py`
- `AiohttpManager`
- `FastAPIManager`
- `FlaskManager`

## Workarounds

Until upgrading:

- Restrict request body size at the reverse proxy or web framework.
- Rate-limit webhook endpoints.
- Reject oversized requests before JSON parsing.

## Solution

Upgrade to **aiosend 3.0.6** or later.

## CWE

- CWE-400: Uncontrolled Resource Consumption

## References
- https://github.com/vovchic17/aiosend/security/advisories/GHSA-7m8f-hgjq-8gc9
- https://github.com/vovchic17/aiosend/commit/db20f0a742209dfac181863d398ec5112687efa4
- https://github.com/vovchic17/aiosend
- https://github.com/vovchic17/aiosend/releases/tag/v3.0.7
