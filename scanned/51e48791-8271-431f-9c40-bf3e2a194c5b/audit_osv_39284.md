# [H] LibVNCClient Tight Gradient decoding allows malicious server-triggered heap/stack OOB writes

## Summary
Severity: High
Advisory: CVE-2026-44988
Aliases: GHSA-jcc5-8wj4-7c58
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44988
Type: osv

## Details
LibVNCClient is a library for easy implementation of a VNC client. In 0.9.15 and earlier, LibVNCClient's Tight encoding decoder uses fixed-size 2048-pixel scratch buffers for the Gradient filter, but it does not reject Tight rectangles whose width is larger than 2048 pixels. A malicious VNC server can send a crafted FramebufferUpdate rectangle using Tight encoding with NoZlib | ExplicitFilter and the Gradient filter. When a LibVNCClient-based client connects, the client processes the server-controlled rectangle width and writes beyond fixed-size Gradient buffers. This vulnerability is fixed with commit 5b270544b85233668b98161323297d418a8f5fd1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44988.json
- https://github.com/LibVNC/libvncserver/security/advisories/GHSA-jcc5-8wj4-7c58
- https://nvd.nist.gov/vuln/detail/CVE-2026-44988
- https://github.com/LibVNC/libvncserver/commit/5b270544b85233668b98161323297d418a8f5fd1
