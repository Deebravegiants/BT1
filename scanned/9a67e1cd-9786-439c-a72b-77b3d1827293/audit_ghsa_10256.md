# [M] OpenClaw: QQ Bot structured payloads could read arbitrary local files

## Summary
Severity: Medium
Advisory: GHSA-846p-hgpv-vphc
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-846p-hgpv-vphc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, QQ Bot structured media payloads could read local files from attacker-chosen paths. A crafted structured payload could escape QQ Bot-owned media roots and cause arbitrary file reads on the host.

## Impact

Prompt-influenced structured payload output could exfiltrate any host file readable by the OpenClaw process through the QQ Bot media-send path. This was a real confidentiality bug on the host filesystem boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `2c45b06afdd6f7c621038b5419d8e661cff34a7f` — restrict QQ Bot structured payload local paths

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @feiyang666 of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-846p-hgpv-vphc
- https://github.com/openclaw/openclaw/commit/2c45b06afdd6f7c621038b5419d8e661cff34a7f
- https://github.com/openclaw/openclaw
