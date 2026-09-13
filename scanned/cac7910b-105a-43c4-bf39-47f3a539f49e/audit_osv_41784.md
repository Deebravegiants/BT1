# [H] mptcp: close TOCTOU race while computing rcv_wnd

## Summary
Severity: High
Advisory: CVE-2026-63867
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63867
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: close TOCTOU race while computing rcv_wnd

The MPTCP output path access locklessly the MPTCP-level ack_seq
in multiple times, using possibly different values for the data_ack
in the DSS option and to compute the announced rcv wnd for the same
packet.

Refactor the cote to avoid inconsistencies which may confuse the
peer. Also ensure that the MPTCP level rcv wnd is updated only when
the egress packet actually contains a DSS ack.

## References
- https://git.kernel.org/stable/c/301a33fd590c408a05c5df800e0cc1e6a8a2f8f8
- https://git.kernel.org/stable/c/3b8cbba7c0ed31189c89f90be247b8973ffa79ef
- https://git.kernel.org/stable/c/68364963e5baf03f16b4420292291f75c8f66497
- https://git.kernel.org/stable/c/8ab24fdebc369c0dfb90f82c1650b1e66662bb45
- https://git.kernel.org/stable/c/8f4f0a157e8436a05bf8c3670b24dbc258911c43
- https://git.kernel.org/stable/c/907ac6b1658e0277f979fcdfae2a753b495c1510
- https://git.kernel.org/stable/c/c4f4cf60797974873dbc8e100144682a6f2f861f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63867.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
