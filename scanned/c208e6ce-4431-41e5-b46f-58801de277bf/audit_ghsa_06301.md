# [M] ep_etherpad-lite: Device-to-device author-token transfer endpoint is replayable, never expires, and exposes the cleartext author token

## Summary
Severity: Medium
Advisory: GHSA-vqfp-p66c-xrp9
CVE: CVE-2026-55088
CWE: CWE-200, CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-vqfp-p66c-xrp9
Type: github-advisory

## Affected
- npm: `ep_etherpad-lite` — affected >=2.6.0 <3.1.0

## Details
Etherpad's device-to-device author-token transfer endpoint is replayable, never expires, and exposes the cleartext author token in the GET response body

## Description

Etherpad ships an endpoint pair under `/tokenTransfer` (`src/node/hooks/express/tokenTransfer.ts`) that lets a logged-in user move their HttpOnly author token to a different browser (typically by scanning a QR code containing the transfer URL). The flow is:

1. **POST `/tokenTransfer`** — the source device sends a request whose own author cookie is read off the server-side cookie jar. The server mints a random UUID and stores the author token (and arbitrary `prefsHttp` field) under a DB key keyed by that UUID. The UUID is returned.
2. **GET `/tokenTransfer/{uuid}`** — the destination device GETs the URL containing the UUID. The server reads the stored record and sets the HttpOnly author cookie on the response.

The original implementation has three serious flaws:

1. **No expiration check.** `createdAt` is written to the record on POST but never inspected on GET. A leaked transfer URL is redeemable indefinitely.
2. **No single-use enforcement.** The DB record is not deleted after a successful GET, so the same URL can be redeemed repeatedly — each redemption yielding a fresh cookie set on whoever issued the GET.
3. **Author token echoed in the response body.** The GET handler ends with `res.send(tokenData)`, which serializes the full record — including the raw author token — into the JSON response. Any JavaScript on the page that issued the GET can read the token, defeating the HttpOnly cookie design that exists specifically to keep the token out of JS reach.

Combined, these mean that any disclosure of a transfer UUID (browser history, mis-shared QR code, screenshot, server log, third-party plugin that proxies the request, an unencrypted intermediate hop) results in **persistent authorship impersonation of the originating account** — the attacker doesn't just get one cookie, they can re-redeem and they get the raw token in cleartext for storage / replay against other endpoints.

## Severity rationale

- **AV:N** — exploitable over the network.
- **AC:H** — requires the attacker to learn the transfer UUID via some out-of-band channel; UUIDs are random.
- **PR:N** — no authentication required at the redemption endpoint.
- **UI:R** — the legitimate user must have issued the POST and the UUID must end up where the attacker can see it (QR code, screenshot, etc.).
- **C:H / I:H** — full author identity takeover (read + write everything that author can).
- **A:N** — no direct denial-of-service.

CVSS lands at 7.5 (High). Some operators may reasonably score this lower (UI:R + AC:H) if their threat model assumes the transfer URL never leaves the user's own device pair.

## Affected versions

- `ep_etherpad-lite >= 2.6.0, <= 3.0.0`. The `/tokenTransfer` endpoint pair was added in [`41cb680` "let user maintain a single session across multiple browsers" (#7228)](https://github.com/ether/etherpad/commit/41cb680), first tagged in **v2.6.0** (2025-11-18). All three flaws (no TTL, no single-use, token in response body) were present from the introducing commit and persisted through `v3.0.0`.

## Patched versions

- `ep_etherpad-lite >= 3.1.0` — the fix is on `develop` HEAD as commit `8c6104c`. Update this field with the actual tagged release version when it ships.

## Proof of concept

```
# 1. Victim posts a transfer from their device.
curl -X POST https://pad.example/tokenTransfer \
  -H 'Cookie: token=t.victim-author-token' \
  -H 'Content-Type: application/json' \
  -d '{"prefsHttp": ""}'
# -> {"id": "1f0b2a3c-..."}

# 2. UUID leaks (browser history, intercepted QR, etc.).
# 3. Attacker redeems it from a totally different machine:
curl -i https://pad.example/tokenTransfer/1f0b2a3c-...
# Headers include:
#   Set-Cookie: token=t.victim-author-token; Path=/; HttpOnly; ...
# Body contains:
#   {"token":"t.victim-author-token", "prefsHttp": "", "createdAt": ...}
#
# Attacker now owns the victim's identity. They can also re-redeem the
# same UUID (no single-use), and the body gives them the cleartext token
# even if the HttpOnly cookie isn't useful to their tooling.
```

## Workarounds

- Disable any UI that surfaces the transfer URL (QR code, copy-button, etc.).
- Reverse-proxy block `/tokenTransfer/*` if device-pairing is not in use.
- Set short DB cleanup intervals (does not address the JS-readable body issue).

None of these workarounds are sufficient on their own — upgrade is the only complete fix.

## Fix

Patched in [`8c6104c`](https://github.com/ether/etherpad/commit/8c6104c) (PR [#7784](https://github.com/ether/etherpad/pull/7784)):

1. **5-minute TTL** (`TRANSFER_TTL_MS`). Records older than this return 410 Gone. Records with absent/non-numeric `createdAt` (legacy records from older code paths) are treated as expired.
2. **Single-use.** The DB record is removed **before** the success response is written, so a parallel request that wins the race observes an already-redeemed transfer rather than a second usable copy.
3. **Body sanitised.** The response body becomes `{ok: true, prefsHttp}` — the raw author token is no longer included. The HttpOnly cookie set in the same response is the only delivery channel.

```diff
- const tokenData = await db.get(`${tokenTransferKey}:${id}`);
+ const key = tokenTransferKey(id);
+ const tokenData: TokenTransferRequest | undefined = await db.get(key);
  if (!tokenData) {
    return res.status(404).send({error: 'Token not found'});
  }
+ await db.remove(key);
+ const createdAt = typeof tokenData.createdAt === 'number'
+     ? tokenData.createdAt : 0;
+ if (Date.now() - createdAt > TRANSFER_TTL_MS) {
+   return res.status(410).send({error: 'Token expired'});
+ }
  ...
- res.send(tokenData);
+ res.send({ok: true, prefsHttp: tokenData.prefsHttp});
```

## Resources

- Patched in: https://github.com/ether/etherpad/pull/7784 (squash commit `8c6104c`).
- Vulnerable code introduced in: https://github.com/ether/etherpad/commit/41cb680 (PR #7228), released in v2.6.0.
- Background on the HttpOnly author-token migration: ether/etherpad PR #7548 (PR3 of #6701, released in v2.7.3). That earlier PR addressed two adjacent issues (the cookie was previously non-HttpOnly, and the POST handler previously trusted the request body for the token value). This GHSA covers only the three flaws that remained after that earlier patch.

## Credits

Reported during an internal security audit by Claude (via @JohnMcLear).

## References
- https://github.com/ether/etherpad/security/advisories/GHSA-vqfp-p66c-xrp9
- https://github.com/ether/etherpad/pull/7784
- https://github.com/ether/etherpad
