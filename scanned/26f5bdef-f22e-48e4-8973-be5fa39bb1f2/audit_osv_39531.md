# [H] rxrpc: Fix rxkad crypto unalignment handling

## Summary
Severity: High
Advisory: CVE-2026-46085
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46085
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix rxkad crypto unalignment handling

Fix handling of a packet with a misaligned crypto length.  Also handle
non-ENOMEM errors from decryption by aborting.  Further, remove the
WARN_ON_ONCE() so that it can't be remotely triggered (a trace line can
still be emitted).

## References
- https://git.kernel.org/stable/c/440d20d95e844b657a93a0b2dcc2aae155efdce6
- https://git.kernel.org/stable/c/af9271eb666d07b6f65612dc160a47f7cb5220ed
- https://git.kernel.org/stable/c/def304aae2edf321d2671fd6ca766a93c21f877e
- https://git.kernel.org/stable/c/f0d3efd03b2a9e0f1ffa6df8fcb264af3d494286
- https://git.kernel.org/stable/c/f1c6bd0cc786a8fa74829ce3c4b3673944a308f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46085.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
