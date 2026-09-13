# [H] netfilter: conntrack: tcp: do not force CLOSE on invalid-seq RST without direction check

## Summary
Severity: High
Advisory: CVE-2026-63913
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63913
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: tcp: do not force CLOSE on invalid-seq RST without direction check

An unintended behavior in the TCP conntrack state machine allows a
connection to be forced into the CLOSE state using an RST packet with an
invalid sequence number.

Specifically, after a SYN packet is observed, an RST with an invalid SEQ
can transition the conntrack entry to TCP_CONNTRACK_CLOSE, regardless of
whether the RST corresponds to the expected reply direction. The relevant
code path assumes the RST is a response to an outgoing SYN, but does not
validate packet direction or ensure that a matching SYN was actually sent
in the opposite direction.

As a result, a crafted packet sequence consisting of a SYN followed by an
invalid-sequence RST can prematurely terminate an active NAT entry. This
makes connection teardown easier than intended.

So, tighten the state transition logic to ensure that RST-triggered
CLOSE transitions only occur when the RST is a valid response to a
previously observed SYN in the correct direction.

## References
- https://git.kernel.org/stable/c/2006979a15af5404bf932a325357683c0bac1656
- https://git.kernel.org/stable/c/2bb6d82b586ea5a4cb73bbdd6b7432e96096bc77
- https://git.kernel.org/stable/c/6476c17d536dbd321c073242e762ddb2713a1238
- https://git.kernel.org/stable/c/b98ab51c45c5608a1c19ce7fd17a3032469bb83f
- https://git.kernel.org/stable/c/bed6e04be8e6b9133d8b16d5a42d0e0ce674fa9a
- https://git.kernel.org/stable/c/d67c6adee8d1b65330d0174c4c367faba14e80a8
- https://git.kernel.org/stable/c/f206def4e86d810f927ba1d8e322ea72b29bce58
- https://git.kernel.org/stable/c/f5547bebc416d56f56fb5b86dc20aabfa42165a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63913.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63913
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
