# [H] ALSA: line6: fix stack overflow in line6_midi_transmit

## Summary
Severity: High
Advisory: CVE-2022-50719
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50719
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.17, >=6.1.0 <6.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: line6: fix stack overflow in line6_midi_transmit

Correctly calculate available space including the size of the chunk
buffer. This fixes a buffer overflow when multiple MIDI sysex
messages are sent to a PODxt device.

## References
- https://git.kernel.org/stable/c/0c76087449ee4ed45a88b10017d02c6694caedb1
- https://git.kernel.org/stable/c/0c9118e381ff538874e00fd4e66a768273c150fb
- https://git.kernel.org/stable/c/25e8c6ecb46843a955f254b8f0d77894e4a53dc4
- https://git.kernel.org/stable/c/389d34c2a8b52acc351fd932ed4bea41fee5a39b
- https://git.kernel.org/stable/c/49cb7737e733013ec86aa77ed2e19b94a68eaa05
- https://git.kernel.org/stable/c/61e4be4a60cc6de723f8c574ddbcb3025eb44cac
- https://git.kernel.org/stable/c/66f359ad66d49f75d39ac729f9114dabf90b81bb
- https://git.kernel.org/stable/c/b026af92b2cea907c780f7168c730c816cd33311
- https://git.kernel.org/stable/c/b8800d324abb50160560c636bfafe2c81001b66c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50719.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50719
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
