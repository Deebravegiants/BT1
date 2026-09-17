# [H] TinyIce: Missing authentication on WebRTC ingest endpoint allows unauthorized stream injection

## Summary
Severity: High
Advisory: GHSA-p7c4-8x34-8j8f
CVE: CVE-2026-45327
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-p7c4-8x34-8j8f
Type: github-advisory

## Affected
- Go: `github.com/DatanoiseTV/tinyice` — affected >=0.8.95 <2.5.0

## Details
## Title

Missing authentication on WebRTC ingest endpoint allows unauthenticated stream injection in TinyIce

## Ecosystem / Package

- **Ecosystem:** `Go` (or "Other" — TinyIce is shipped as a Go binary, not a Go module published to a registry)
- **Package name:** `github.com/DatanoiseTV/tinyice`

## Affected versions

```
>= 0.8.95, <= 2.4.1
```

(Introduced 2026-02-21 in commit `e2b60d6` — "debug: add Go Live connection tracing and backend data flow logging" — when `handleWebRTCSourceOffer` was registered at `/webrtc/source-offer` without an authentication check. Every tagged release from `v0.8.95` through `v2.4.1` ships the vulnerable handler.)

## Patched versions

```
>= 2.5.0
```

## Severity

- **CVSS 3.1 base score:** 7.4 (High)
- **CVSS vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L`
- **CWE:** [CWE-306: Missing Authentication for Critical Function](https://cwe.mitre.org/data/definitions/306.html)

## Description

TinyIce's WebRTC source-ingest HTTP endpoint, `POST /webrtc/source-offer?mount=<mount>`, accepted any inbound WebRTC SDP offer with no authentication check. The handler routed the offer to `WebRTCManager.HandleSourceOffer`, which then accepted whatever audio/video tracks the peer published and broadcast them on the named mount as if they were the legitimate source.

The other ingest paths (`POST /<mount>` over HTTP/1 with the icecast `SOURCE` / `PUT` verb, RTMP, SRT) all require the per-mount source password, falling back to `default_source_password` from the config. The WebRTC ingest path didn't.

## Impact

A network attacker who can reach the TinyIce HTTP port can:

1. Identify a target mount (mount names are public — they appear in the directory listing, the player URL, and the YP listing).
2. Negotiate a WebRTC peer connection with the server.
3. Publish arbitrary Opus / H.264 to that mount.
4. Have it broadcast to every listener on the mount.

This is a high-integrity-impact issue: an attacker can replace a radio's broadcast with their own audio (silence, noise, malicious content, branded competitor content, etc.). Listeners hear what the attacker sends, not what the legitimate publisher intended.

The legitimate publisher can re-establish their session — TinyIce's source-takeover handshake gives the new offer priority once it arrives, with a 3-second drain of the previous pump goroutine — but the attacker can in principle re-connect immediately after, producing a sustained broadcast hijack until the operator manually intervenes (block at firewall, rotate source passwords once the patch is applied, restart the service).

There is no direct confidentiality impact through this endpoint: the attacker doesn't gain access to listener data or other mounts' content.

## Workarounds

If users cannot upgrade immediately:

- **Recommended:** block `POST /webrtc/source-offer` at the reverse proxy in front of TinyIce. The endpoint has no production use case for clients outside the operator's own administration — disabling it loses no functionality unless the consuming application specifically use the browser-based "go-live" feature.
- Restrict TinyIce's HTTP port to a trusted network (VPN, internal LAN). Listener access can still be served via a separately-firewalled CDN if the application needs public listening.

## Detection

To check whether an application's deployment is exposed, run from outside the network:

```
curl -i -X POST 'https://your-tinyice-host/webrtc/source-offer?mount=/anymount' \
  -H 'Content-Type: application/json' \
  -d '{"type":"offer","sdp":"v=0\r\n"}'
```

- If the response is `400 Bad Request` with a JSON body containing an SDP-parsing error from `pion/webrtc`, **a consuming application is vulnerable** — the server tried to negotiate the (malformed) offer without asking for credentials.
- If the response is `401 Unauthorized` (Basic auth challenge), the consuming application has been patched.

Authenticated log lines on a patched server will look like:

```
WARN  Authentication failed for user 'webrtc-source' from 1.2.3.4: invalid source password
```

## Fix

Upstream commit: [`8067d6b`](https://github.com/DatanoiseTV/tinyice/commit/8067d6b) "fix(api): require source password on /webrtc/source-offer + CSRF/access on /go-live-chunk".

The handler now:

1. Requires either HTTP Basic auth or a `?password=` query parameter.
2. Compares the supplied password against the per-mount source password (or the `default_source_password` fallback) using bcrypt.
3. Hooks into the existing brute-force IP rate-limiter (5 failed attempts per IP within 15 minutes triggers a lockout).
4. Rejects requests for mounts in `disabled_mounts`.

The same release also tightens an adjacent endpoint, `POST /admin/golive/chunk`, which previously required session authentication but did not verify the session user's per-mount access nor check the CSRF token.

## Timeline

- 2026-02-21 — Vulnerable handler introduced (`e2b60d6`).
- 2026-05-09 — Vulnerability identified during a maintainer-led audit.
- 2026-05-09 — Patched in commit `8067d6b`, released as `v2.5.0`.
- 2026-05-09 — GitHub Security Advisory published, CVE assigned.

## References
- https://github.com/DatanoiseTV/tinyice/security/advisories/GHSA-p7c4-8x34-8j8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45327
- https://github.com/DatanoiseTV/tinyice/commit/8067d6b
- https://github.com/DatanoiseTV/tinyice
- https://github.com/DatanoiseTV/tinyice/releases/tag/v2.5.0
