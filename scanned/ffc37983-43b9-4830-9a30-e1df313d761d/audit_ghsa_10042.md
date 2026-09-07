# [M] OpenClaw: Webchat audio embedding could read local files without local-root containment

## Summary
Severity: Medium
Advisory: GHSA-gfg9-5357-hv4c
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-gfg9-5357-hv4c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.15

## Details
## Impact

OpenClaw deployments before `2026.4.15` could embed host-local audio files into webchat responses without applying the local media root containment check used by other media-serving paths.

If an attacker could influence an agent or tool-produced `ReplyPayload.mediaUrl`, the webchat audio embedding helper could resolve an absolute local path or `file:` URL, read an audio-like file under the size cap, and base64-encode it into the webchat media response. This crossed the model/tool-output boundary into a host file read. Prompt injection or malicious tool output is a delivery mechanism; the security boundary failure is the missing local-root containment check.

The impact is narrow: the file had to be readable by the gateway process, have an audio-like extension, and fit within the webchat audio size cap. The issue exposed contents into the webchat assistant/media transcript path; it was not a general remote filesystem API.

## Affected Packages / Versions

- Package: `openclaw` on npm
- Affected versions: `<= 2026.4.14`
- Patched version: `2026.4.15`

The latest public release, `2026.4.21`, also contains the fix.

## Patches

The public fix threads the applicable local media roots into the webchat audio embedding path and calls `assertLocalMediaAllowed` before local audio content is read. Current `main` also includes an additional `trustedLocalMedia` gate so untrusted model/tool payloads cannot opt into local audio embedding.

Fix commit:

- `6e58f1f9f54bca1fea1268ec0ee4c01a2af03dde`

## Workarounds

Upgrade to `openclaw@2026.4.15` or later. The latest public release, `2026.4.21`, is fixed. Before upgrading, avoid exposing webchat sessions to untrusted prompt/tool content that can influence reply media URLs.

## Credits

OpenClaw thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gfg9-5357-hv4c
- https://github.com/openclaw/openclaw/commit/6e58f1f9f54bca1fea1268ec0ee4c01a2af03dde
- https://github.com/openclaw/openclaw
