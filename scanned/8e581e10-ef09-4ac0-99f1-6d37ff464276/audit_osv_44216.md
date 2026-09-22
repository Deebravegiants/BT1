# [H] batman-adv: gw: acquire ethernet header only after skb realloc

## Summary
Severity: High
Advisory: CVE-2026-80601
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80601
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: gw: acquire ethernet header only after skb realloc

The pskb_may_pull() called by batadv_get_vid() could reallocate the buffer
behind the skb. Variables which were pointing to the old buffer need to be
reassigned to avoid an use-after-free.

## References
- https://git.kernel.org/stable/c/2760b38222c8828b075802342fe3b91eb823d542
- https://git.kernel.org/stable/c/6c37f1166549c999ccd164b0cb6462d1ae68f8f6
- https://git.kernel.org/stable/c/77880a3be88d378d60cc1e8f8ec70430e2ed0518
- https://git.kernel.org/stable/c/916dac5f2944f63f07f7b501acbea6737dbbed0e
- https://git.kernel.org/stable/c/afac8096bde4948e3caa7e4dd733867cfbd3018e
- https://git.kernel.org/stable/c/b79884a5567bf788fb76c30832467cf6a56f3c0d
- https://git.kernel.org/stable/c/e3f4325e35dd6e76b80665f3510738ce34819753
- https://git.kernel.org/stable/c/e6b43acd34b219b807e65096ce207b087942779d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80601.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80601
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
