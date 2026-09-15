# [H] wifi: wilc1000: fix potential RCU dereference issue in wilc_parse_join_bss_param

## Summary
Severity: High
Advisory: CVE-2024-47712
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47712
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.9.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: fix potential RCU dereference issue in wilc_parse_join_bss_param

In the `wilc_parse_join_bss_param` function, the TSF field of the `ies`
structure is accessed after the RCU read-side critical section is
unlocked. According to RCU usage rules, this is illegal. Reusing this
pointer can lead to unpredictable behavior, including accessing memory
that has been updated or causing use-after-free issues.

This possible bug was identified using a static analysis tool developed
by myself, specifically designed to detect RCU-related issues.

To address this, the TSF value is now stored in a local variable
`ies_tsf` before the RCU lock is released. The `param->tsf_lo` field is
then assigned using this local variable, ensuring that the TSF value is
safely accessed.

## References
- https://git.kernel.org/stable/c/2f944e6255c2fc1c9bd9ee32f6b14ee0b2a51eb5
- https://git.kernel.org/stable/c/557418e1704605a81c9e26732449f71b1d40ba1e
- https://git.kernel.org/stable/c/5a24cedc243ace5ed7c1016f52a7bfc8f5b07815
- https://git.kernel.org/stable/c/6d7c6ae1efb1ff68bc01d79d94fdf0388f86cdd8
- https://git.kernel.org/stable/c/79510414a7626317f13cc9073244ab7a8deb3192
- https://git.kernel.org/stable/c/84398204c5df5aaf89453056cf0647cda9664d2b
- https://git.kernel.org/stable/c/b040b71d99ee5e17bb7a743dc01cbfcae8908ce1
- https://git.kernel.org/stable/c/bf090f4fe935294361eabd9dc5a949fdd77d3d1b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47712.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
