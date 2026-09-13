# [H] ASoC: codecs: wcd938x: fix incorrect used of portid

## Summary
Severity: High
Advisory: CVE-2022-48716
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: wcd938x: fix incorrect used of portid

Mixer controls have the channel id in mixer->reg, which is not same
as port id. port id should be derived from chan_info array.
So fix this. Without this, its possible that we could corrupt
struct wcd938x_sdw_priv by accessing port_map array out of range
with channel id instead of port id.

## References
- https://git.kernel.org/stable/c/9167f2712dc8c24964840a4d1e2ebf130e846b95
- https://git.kernel.org/stable/c/aa7152f9f117b3e66b3c0d4158ca4c6d46ab229f
- https://git.kernel.org/stable/c/c5c1546a654f613e291a7c5d6f3660fc1eb6d0c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48716.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
