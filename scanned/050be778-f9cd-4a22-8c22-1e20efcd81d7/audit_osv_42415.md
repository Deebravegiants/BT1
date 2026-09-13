# [H] drm/amdgpu/vcn4: avoid rereading IB param length

## Summary
Severity: High
Advisory: CVE-2026-68107
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68107
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.17.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vcn4: avoid rereading IB param length

Reuse the parameter length returned by
vcn_v4_0_enc_find_ib_param() instead of rereading it from
the IB.

This avoids a potential TOCTOU issue if the IB contents
change between reads.

(cherry picked from commit dbb02b4755f8c1f3773263f2d779872c1c0c073a)

## References
- https://git.kernel.org/stable/c/3b4082fabc67c9780b06eb959e59dd92fa79c0f0
- https://git.kernel.org/stable/c/bbbe6a2a8d8dc87243438d3ffea2083b52d882d9
- https://git.kernel.org/stable/c/bd868c077f67589ed2a714307ceaade5f246e302
- https://git.kernel.org/stable/c/c309626bf91fa0a0b583575654e6e14e81f818a3
- https://git.kernel.org/stable/c/ff6aa542d91d76a185f69bd1997b94a560ff5f6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68107.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
