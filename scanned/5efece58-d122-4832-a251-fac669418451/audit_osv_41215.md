# [M] CVE-2026-58374

## Summary
Severity: Medium
Advisory: CVE-2026-58374
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58374
Type: osv

## Details
In hostapd before 2.12, a missing bounds check in AP-mode Wi-Fi 7 (IEEE 802.11be) Multi-Link Operation (MLO) association request processing allows an unauthenticated attacker within wireless range to send a crafted management frame containing a malformed Multi-Link Element or Per-STA Profile subelement. In hostapd_process_ml_assoc_req() in src/ap/ieee802_11_eht.c, the received link_id field can be parsed as value 15, but the corresponding links[] storage only has valid entries for lower link IDs (0 through 14). This causes an out-of-bounds write / small memory corruption during association processing before the 4-way handshake. The attack does not require network credentials, prior authentication, or user interaction. The confirmed practical impact is denial of service through hostapd process termination. This affects hostapd v2.11 and newer development snapshots before v2.12 when built with CONFIG_IEEE80211BE enabled. The issue is fixed in hostapd v2.12 and the upstream 2026-1 fixes.

## References
- https://www.openwall.com/lists/oss-security/2026/06/30/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58374
- https://w1.fi/security/2026-1/missing-ml-parsing-validation.txt
- https://git.w1.fi/cgit/hostap/commit/?id=46dd5a4ffc9bcf44cf8fc45120b3e1e5ec922187
- https://git.w1.fi/cgit/hostap/commit/?id=aa9d345887389a251c63a3781d2ad2940d079193
- https://w1.fi/security/2026-1/
