# [H] drm/i915/hdcp: check streams[] bounds before overflow

## Summary
Severity: High
Advisory: CVE-2026-68253
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68253
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/hdcp: check streams[] bounds before overflow

The data->streams[] overflow check is done after the buffer overflow has
already happened. Move the overflow check before the write.

Side note, emitting a warning splat with a backtrace might be overkill
here, but prefer not changing the behaviour other than not doing the
overrun.

Discovered using AI-assisted static analysis confirmed by Intel Product
Security.

(cherry picked from commit 9284ab3b6e776c315883ac2611283d263c9460fd)

## References
- https://git.kernel.org/stable/c/2106fb490b2c6003e23ad6ff36ce823a2170e138
- https://git.kernel.org/stable/c/336cf6d80d41457442b659e7ba7a7badc0ffe79d
- https://git.kernel.org/stable/c/389079bf04e6f0c6f10f5b879f6d7a9cf80f0567
- https://git.kernel.org/stable/c/3d2ef8d389495e7889c6062d8bddc46d2a5fbdef
- https://git.kernel.org/stable/c/84351f12390349ba010920fc247e1a0b12e41eb3
- https://git.kernel.org/stable/c/984085c5b53572e2e03fd5fc4817e86ef1effc6e
- https://git.kernel.org/stable/c/bbb15a6b042d02e5508a02b4847e02d2579ee7bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
