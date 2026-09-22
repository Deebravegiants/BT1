# [C] wifi: mac80211: don't return unset power in ieee80211_get_tx_power()

## Summary
Severity: Critical
Advisory: CVE-2023-52832
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52832
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: don't return unset power in ieee80211_get_tx_power()

We can get a UBSAN warning if ieee80211_get_tx_power() returns the
INT_MIN value mac80211 internally uses for "unset power level".

 UBSAN: signed-integer-overflow in net/wireless/nl80211.c:3816:5
 -2147483648 * 100 cannot be represented in type 'int'
 CPU: 0 PID: 20433 Comm: insmod Tainted: G        WC OE
 Call Trace:
  dump_stack+0x74/0x92
  ubsan_epilogue+0x9/0x50
  handle_overflow+0x8d/0xd0
  __ubsan_handle_mul_overflow+0xe/0x10
  nl80211_send_iface+0x688/0x6b0 [cfg80211]
  [...]
  cfg80211_register_wdev+0x78/0xb0 [cfg80211]
  cfg80211_netdev_notifier_call+0x200/0x620 [cfg80211]
  [...]
  ieee80211_if_add+0x60e/0x8f0 [mac80211]
  ieee80211_register_hw+0xda5/0x1170 [mac80211]

In this case, simply return an error instead, to indicate
that no data is available.

## References
- https://git.kernel.org/stable/c/1571120c44dbe5757aee1612c5b6097cdc42710f
- https://git.kernel.org/stable/c/21a0f310a9f3bfd2b4cf4f382430e638607db846
- https://git.kernel.org/stable/c/298e767362cade639b7121ecb3cc5345b6529f62
- https://git.kernel.org/stable/c/2be24c47ac19bf639c48c082486c08888bd603c6
- https://git.kernel.org/stable/c/5a94cffe90e20e8fade0b9abd4370bd671fe87c7
- https://git.kernel.org/stable/c/717de20abdcd1d4993fa450e28b8086a352620ea
- https://git.kernel.org/stable/c/adc2474d823fe81d8da759207f4f1d3691aa775a
- https://git.kernel.org/stable/c/e160ab85166e77347d0cbe5149045cb25e83937f
- https://git.kernel.org/stable/c/efeae5f4972f75d50002bc50eb112ab9e7069b18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52832.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52832
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
