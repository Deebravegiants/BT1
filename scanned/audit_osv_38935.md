# [H] wifi: wl1251: validate packet IDs before indexing tx_frames

## Summary
Severity: High
Advisory: CVE-2026-43113
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43113
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wl1251: validate packet IDs before indexing tx_frames

wl1251_tx_packet_cb() uses the firmware completion ID directly to index
the fixed 16-entry wl->tx_frames[] array. The ID is a raw u8 from the
completion block, and the callback does not currently verify that it
fits the array before dereferencing it.

Reject completion IDs that fall outside wl->tx_frames[] and keep the
existing NULL check in the same guard. This keeps the fix local to the
trust boundary and avoids touching the rest of the completion flow.

## References
- https://git.kernel.org/stable/c/0fd56fad9c56356e7fa7a7c52e7ecbf807a44eb0
- https://git.kernel.org/stable/c/26ee518695c484f75e3606d631278e84bd24ae02
- https://git.kernel.org/stable/c/6509dbece7339dbc8980c706b9d623119a6de105
- https://git.kernel.org/stable/c/8d7465be5163a923ee5d7459719ef5a021c1584a
- https://git.kernel.org/stable/c/a8a11a876f0a97061ee5d9e61d0f5a0df7e241c7
- https://git.kernel.org/stable/c/b6ba1eacf276063ebeefbbae8056043c24f2efaf
- https://git.kernel.org/stable/c/df15adc692a802636dd3f258fc7cca8bf7a0ed9a
- https://git.kernel.org/stable/c/e0dc1ad870d6788b049bfe1511ac75b2333a7550
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43113
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
