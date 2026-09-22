# [M] CVE-2026-0716

## Summary
Severity: Medium
Advisory: CVE-2026-0716
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2026-0716
Type: osv

## Details
A flaw was found in libsoup’s WebSocket frame processing when handling incoming messages. If a non-default configuration is used where the maximum incoming payload size is unset, the library may read memory outside the intended bounds. This can cause unintended memory exposure or a crash. Applications using libsoup’s WebSocket support with this configuration may be impacted.

## References
- https://access.redhat.com/security/cve/CVE-2026-0716
- https://bugzilla.redhat.com/show_bug.cgi?id=2427896
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/476
