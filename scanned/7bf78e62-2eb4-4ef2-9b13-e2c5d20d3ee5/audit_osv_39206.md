# [C] soundcloud-rpc: Remote Code Execution via XSS in Track Title

## Summary
Severity: Critical
Advisory: CVE-2026-44482
Aliases: GHSA-p37x-32p8-445f
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44482
Type: osv

## Details
soundcloud-rpc is a SoundCloud Client with Discord Rich Presence, Dark Mode, Last.fm and AdBlock support. Prior to 0.1.8, a track title containing an HTML payload executed locally in the Electron app. This means attacker-controlled SoundCloud track metadata can lead to local command execution on the user's machine. The application exposes a preload API (window.soundcloudAPI.sendTrackUpdate) to the remote SoundCloud page. Track metadata from SoundCloud is trusted and forwarded through IPC into the Electron main process. The app later renders that metadata as raw HTML inside privileged Electron views that have Node.js integration enabled. This vulnerability is fixed in 0.1.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44482.json
- https://github.com/richardhbtz/soundcloud-rpc/security/advisories/GHSA-p37x-32p8-445f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44482
