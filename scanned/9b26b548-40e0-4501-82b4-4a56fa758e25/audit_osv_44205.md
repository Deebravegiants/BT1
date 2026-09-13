# [C] mptcp: options: reset DSS fields in case of unexpected size

## Summary
Severity: Critical
Advisory: CVE-2026-80586
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80586
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: options: reset DSS fields in case of unexpected size

A remote peer could send a malformed DSS with a wrong size, followed by
another DSS or MPC + Data. In this case, the first suboption will be
ignored, but leaving some fields written, which could lead to
inconsistency or access uninitialized data.

Explicitly reset the fields that could have been modified in case of
unexpected size.

## References
- https://git.kernel.org/stable/c/15e35fdad7a5576bf3f1c8d688877aeb5d1b506b
- https://git.kernel.org/stable/c/192878df582c51d440bf7b91a15f297f29f2b596
- https://git.kernel.org/stable/c/1fade1b2ac5b1a4948e538fae7313bea57b5ac36
- https://git.kernel.org/stable/c/26dac5c9ffb20812b475fdf253eb04fab99cff3b
- https://git.kernel.org/stable/c/27ed642a4e7e4b5df4b8522c72c457a67e052493
- https://git.kernel.org/stable/c/35772b4981f38ba8059372cde8753e8e477e98ec
- https://git.kernel.org/stable/c/4e80eff5c1c893aca2ac1d202f0b256d2e52ecde
- https://git.kernel.org/stable/c/b1256090816ec46011601e084be580731df58fc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80586.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
