# [H] java-client Allows Network Pivot via Unvalidated directConnect Redirect in AppiumCommandExecutor

## Summary
Severity: High
Advisory: GHSA-28f5-38xr-jh2w
CVE: CVE-2026-43910
CWE: CWE-441, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-28f5-38xr-jh2w
Type: github-advisory

## Affected
- Maven: `io.appium:java-client` — affected >=8.2.1 <10.1.1

## Details
## Summary

When `directConnect(true)` is enabled, appium/java-client unconditionally
accepts `directConnectHost`, `directConnectPort`, and `directConnectPath`
from the server's NEW_SESSION response and silently redirects all subsequent
session traffic to the attacker-specified endpoint — with no allowlist,
no host validation, and no user notification.

## Affected Code

- `AppiumCommandExecutor.java` (line 196–219): `setDirectConnect()` builds
  a new URL from server-supplied fields and calls `overrideServerUrl(newUrl)`
  without validating host/IP.
- `DirectConnect.java`: `getUrl()` constructs `protocol://host:port/path`
  with no allowlist.

## Root Cause

Only the protocol is validated (must equal "https"). The destination host
and port are never checked against any allowlist or denylist.

## PoC (confirmed)

A rogue server injecting `directConnectHost=127.0.0.1:4443` causes the
client to silently redirect all post-session commands:

[bootstrap]       POST /wd/hub/session
[bootstrap]       Injecting directConnect -> https://127.0.0.1:4443/wd/hub
[redirect-target] HIT #1: GET /wd/hub/session/poc-session-001/source
[redirect-target] HIT #2: DELETE /wd/hub/session/poc-session-001

Original source code unmodified — confirmed via `git diff HEAD` (empty).

## Evidence Screenshots

**Screenshot 1 — Rogue server capturing redirected traffic:**

<img width="887" height="146" alt="1" src="https://github.com/user-attachments/assets/cc28002c-ea20-4ac8-8336-cec632e3c842" />

**Screenshot 2 — Java client processing response from attacker host:**

<img width="788" height="130" alt="2" src="https://github.com/user-attachments/assets/222cbab0-0d53-45b2-847d-6aa4e3b79370" />

## Impact

- Full interception of session traffic
- Network pivot to internal hosts (RFC-1918, 169.254.169.254)
- Cloud credential theft via IMDS endpoint
- Escalates to ~8.1 High in CI/CD environments where directConnect(true)
  is set in shared base configuration

## Suggested Fix

Add allowlist validation before `overrideServerUrl()` is called, and/or
block RFC-1918/loopback/link-local destinations by default.

[poc_appium_directconnect.zip](https://github.com/user-attachments/files/26472525/poc_appium_directconnect.zip)

## References
- https://github.com/appium/java-client/security/advisories/GHSA-28f5-38xr-jh2w
- https://github.com/appium/java-client/pull/2408
- https://github.com/appium/java-client/commit/2b9cd442b9dbf56ccc6f1e83aeeb411c0ec230c9
- https://github.com/appium/java-client
- https://github.com/appium/java-client/releases/tag/v10.1.1
