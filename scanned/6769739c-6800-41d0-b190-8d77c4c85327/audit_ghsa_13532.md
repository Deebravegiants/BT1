# [H] github.com/nghttp2/nghttp2 has HTTP/2 Rapid Reset

## Summary
Severity: High
Advisory: GHSA-vx74-f528-fxqg
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-vx74-f528-fxqg
Type: github-advisory

## Affected
- Go: `github.com/nghttp2/nghttp2` — affected >=0 <1.57.0

## Details
### Impact

Rapidly creating and cancelling streams (HEADERS frame immediately followed by RST_STREAM) without bound cause denial of service.

See https://www.cve.org/CVERecord?id=CVE-2023-44487 for details.

### Patches

nghttp2 v1.57.0 mitigates this vulnerability by default.

### Workarounds

If upgrading to nghttp2 v1.57.0 is not possible, implement `nghttp2_on_frame_recv_callback`, and check and count RST_STREAM frames.  If excessive number of RST_STREAM are received, then take action, such as dropping connection silently, or call `nghttp2_submit_goaway` and gracefully terminate the connection.

### References

The following commit mitigates this vulnerability:

- https://github.com/nghttp2/nghttp2/commit/72b4af6143681f528f1d237b21a9a7aee1738832

## References
- https://github.com/nghttp2/nghttp2/security/advisories/GHSA-vx74-f528-fxqg
- https://github.com/nghttp2/nghttp2/commit/72b4af6143681f528f1d237b21a9a7aee1738832
- https://github.com/nghttp2/nghttp2
- https://github.com/nghttp2/nghttp2/releases/tag/v1.57.0
