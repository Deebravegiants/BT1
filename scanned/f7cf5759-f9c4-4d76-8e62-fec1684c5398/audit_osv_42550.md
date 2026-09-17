# [H] wifi: cfg80211: bound element ID read when checking non-inheritance

## Summary
Severity: High
Advisory: CVE-2026-68402
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68402
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: bound element ID read when checking non-inheritance

cfg80211_is_element_inherited() reads the first data octet of the
candidate element (id = elem->data[0]) to look it up in an extension
non-inheritance list. It does so after testing elem->id, but without
verifying that the element actually has a data octet. A zero-length
extension element (WLAN_EID_EXTENSION with length 0) therefore makes it
read one octet past the end of the element.

_ieee802_11_parse_elems_full() runs this check for every element of a
frame once a non-inheritance context exists -- e.g. while parsing a
per-STA profile of a Multi-Link element in a (re)association response,
or a non-transmitted BSS profile -- so a crafted frame from an AP can
trigger a one-octet slab-out-of-bounds read during element parsing:

  BUG: KASAN: slab-out-of-bounds in cfg80211_is_element_inherited
  Read of size 1 ... in net/wireless/scan.c

Return early (treat the element as inherited) when an extension element
carries no data, mirroring the existing handling of empty ID lists.

The bug was found by fuzzing ieee802_11_parse_elems_full() under KASAN.

## References
- https://git.kernel.org/stable/c/11ac7a5e75f5132f1778e0c60981d30dc29fb869
- https://git.kernel.org/stable/c/20c308d9a57722801961f816395bf825f7bde6bc
- https://git.kernel.org/stable/c/24154c172246ae3f0e69bb17c9111095685ceedc
- https://git.kernel.org/stable/c/2d31ebb26a14f103c9cdc5287fb20cb2d4bde901
- https://git.kernel.org/stable/c/521dd5fe6d12b0d3c275f919738dc3a07117f4a5
- https://git.kernel.org/stable/c/84bd907361c56fbd5523eceb2682cb39da059bd5
- https://git.kernel.org/stable/c/cb8afea4655ff004fa7feee825d5c79783525383
- https://git.kernel.org/stable/c/ddf2773bcc8e49a43c561f22ec1e7924215d7947
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68402.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
