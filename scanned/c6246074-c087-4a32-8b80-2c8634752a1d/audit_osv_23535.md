# [H] qede: confirm skb is allocated before using

## Summary
Severity: High
Advisory: CVE-2022-49084
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49084
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

qede: confirm skb is allocated before using

qede_build_skb() assumes build_skb() always works and goes straight
to skb_reserve(). However, build_skb() can fail under memory pressure.
This results in a kernel panic because the skb to reserve is NULL.

Add a check in case build_skb() failed to allocate and return NULL.

The NULL return is handled correctly in callers to qede_build_skb().

## References
- https://git.kernel.org/stable/c/034a92c6a81048128fc7b18d278d52438a13902a
- https://git.kernel.org/stable/c/4e910dbe36508654a896d5735b318c0b88172570
- https://git.kernel.org/stable/c/8928239e5e2e460d95b8a0b89f61671625e7ece0
- https://git.kernel.org/stable/c/9648adb1b3ece55c657d3a4f52bfee663b710dfe
- https://git.kernel.org/stable/c/b2d6b3db9d1cf80908964036dbe1c52a86b1afb1
- https://git.kernel.org/stable/c/c9bdce2359b5f4986eb38d1e81865b3586cc20d2
- https://git.kernel.org/stable/c/e1fd0c42acfa22bb34d2ab6a111484f466ab8093
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49084.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
