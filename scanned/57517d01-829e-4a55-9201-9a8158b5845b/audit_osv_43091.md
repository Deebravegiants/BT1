# [H] ALSA: usb-audio: qcom: reject stream disable with no active interface

## Summary
Severity: High
Advisory: CVE-2026-72446
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72446
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: qcom: reject stream disable with no active interface

handle_uaudio_stream_req() resolves an interface index with
info_idx_from_ifnum(), which returns -EINVAL when no interface matches.
The enable branch and the response: cleanup label both guard against a
negative index, but the disable branch does not: it forms
info = &uadev[pcm_card_num].info[info_idx] and dereferences it.

uadev[].info is a pointer allocated only when a stream is first enabled,
so a negative info_idx on the disable path is unsafe in two ways:

 - If the card was never enabled, .info is NULL and &info[-EINVAL] is a
   wild pointer; reading info->data_ep_pipe faults (kernel oops).

 - If the card was enabled at least once (.info allocated) and the
   disable names an interface that does not match, &info[-EINVAL] points
   before the allocation; info->data_ep_pipe / info->sync_ep_pipe are an
   out-of-bounds slab read and, when non-zero, an out-of-bounds 4-byte
   write (both pipe fields are cleared to 0). That is memory corruption,
   not just a NULL dereference.

The request is reachable from unprivileged local userspace over
AF_QIPCRTR. Reject a disable request with no resolved interface, matching
the guard the enable path already has.

## References
- https://git.kernel.org/stable/c/25a867aa5e67a84333fa6e5c21292c5bcff86b90
- https://git.kernel.org/stable/c/a22356d1f731553e99aa2707dbd38c659bdd28d8
- https://git.kernel.org/stable/c/bdb640be82e645e2828731648f485224d0c2587b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
