# [H] wifi: nl80211: fix integer overflow in nl80211_parse_mbssid_elems()

## Summary
Severity: High
Advisory: CVE-2023-53570
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53570
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: fix integer overflow in nl80211_parse_mbssid_elems()

nl80211_parse_mbssid_elems() uses a u8 variable num_elems to count the
number of MBSSID elements in the nested netlink attribute attrs, which can
lead to an integer overflow if a user of the nl80211 interface specifies
256 or more elements in the corresponding attribute in userspace. The
integer overflow can lead to a heap buffer overflow as num_elems determines
the size of the trailing array in elems, and this array is thereafter
written to for each element in attrs.

Note that this vulnerability only affects devices with the
wiphy->mbssid_max_interfaces member set for the wireless physical device
struct in the device driver, and can only be triggered by a process with
CAP_NET_ADMIN capabilities.

Fix this by checking for a maximum of 255 elements in attrs.

## References
- https://git.kernel.org/stable/c/6311071a056272e1e761de8d0305e87cc566f734
- https://git.kernel.org/stable/c/7d09f9f255a5f78578deba5454923072bb53b16c
- https://git.kernel.org/stable/c/e642eb67b8c10dcce758d549cc81564116e0fa49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53570.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
