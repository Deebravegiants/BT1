# [H] wifi: mac80211: limit injected antenna index in ieee80211_parse_tx_radiotap

## Summary
Severity: High
Advisory: CVE-2026-63869
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63869
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: limit injected antenna index in ieee80211_parse_tx_radiotap

When parsing the radiotap header of an injected frame,
ieee80211_parse_tx_radiotap() uses the IEEE80211_RADIOTAP_ANTENNA value
directly as a shift count:

	info->control.antennas |= BIT(*iterator.this_arg);

*iterator.this_arg is an 8-bit value taken straight from the frame
supplied by userspace, so BIT() can be asked to shift by up to 255. That
is undefined behaviour on the unsigned long and is reported by UBSAN:

  UBSAN: shift-out-of-bounds in net/mac80211/tx.c:2174:30
  shift exponent 235 is too large for 64-bit type 'unsigned long'
  Call Trace:
   ieee80211_parse_tx_radiotap+0xadb/0x1950 net/mac80211/tx.c:2174
   ieee80211_monitor_start_xmit+0xb1f/0x1250 net/mac80211/tx.c:2451
   ...
   packet_sendmsg+0x3eb6/0x50f0 net/packet/af_packet.c:3109

info->control.antennas is a 2-bit bitmap (u8 antennas:2), so only antenna
indices 0 and 1 can ever be represented. Ignore any larger value instead
of shifting out of bounds.

## References
- https://git.kernel.org/stable/c/033ce021a220913ac02416fcb5ac883a9ff8b6c7
- https://git.kernel.org/stable/c/6c0cf89f36ac0c0fd8687a4ccdce2efb23a9c663
- https://git.kernel.org/stable/c/9b40c59bab08f2a99abf969cc0bb92fa49de004b
- https://git.kernel.org/stable/c/f6d3dc8e8492bf8435e0b23c99472af7bafd6b44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63869.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
