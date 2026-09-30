# [H] ALSA: firewire-motu: add bounds check in put_user loop for DSP events

## Summary
Severity: High
Advisory: CVE-2025-68753
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-68753
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: firewire-motu: add bounds check in put_user loop for DSP events

In the DSP event handling code, a put_user() loop copies event data.
When the user buffer size is not aligned to 4 bytes, it could overwrite
beyond the buffer boundary.

Fix by adding a bounds check before put_user().

## References
- https://git.kernel.org/stable/c/0d71b3c2ed742f1ccb3b0b7a61afb90c0251093f
- https://git.kernel.org/stable/c/298e753880b6ea99ac30df34959a7a03b0878eed
- https://git.kernel.org/stable/c/6d4f17782ce4facf3197e79707df411ee3d7b30a
- https://git.kernel.org/stable/c/8f9e51cf2a2a43d0cd72d3dc0b5ccea3f639c187
- https://git.kernel.org/stable/c/df692cf2b601a54b34edfdb9e683d67483aa8ce1
- https://git.kernel.org/stable/c/ea2c921d9de6e32ca50cb817b9d57bb881be70de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68753.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
