# [H] wifi: mac80211: Discard Beacon frames to non-broadcast address

## Summary
Severity: High
Advisory: CVE-2025-71127
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71127
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.65, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: Discard Beacon frames to non-broadcast address

Beacon frames are required to be sent to the broadcast address, see IEEE
Std 802.11-2020, 11.1.3.1 ("The Address 1 field of the Beacon .. frame
shall be set to the broadcast address"). A unicast Beacon frame might be
used as a targeted attack to get one of the associated STAs to do
something (e.g., using CSA to move it to another channel). As such, it
is better have strict filtering for this on the received side and
discard all Beacon frames that are sent to an unexpected address.

This is even more important for cases where beacon protection is used.
The current implementation in mac80211 is correctly discarding unicast
Beacon frames if the Protected Frame bit in the Frame Control field is
set to 0. However, if that bit is set to 1, the logic used for checking
for configured BIGTK(s) does not actually work. If the driver does not
have logic for dropping unicast Beacon frames with Protected Frame bit
1, these frames would be accepted in mac80211 processing as valid Beacon
frames even though they are not protected. This would allow beacon
protection to be bypassed. While the logic for checking beacon
protection could be extended to cover this corner case, a more generic
check for discard all Beacon frames based on A1=unicast address covers
this without needing additional changes.

Address all these issues by dropping received Beacon frames if they are
sent to a non-broadcast address.

## References
- https://git.kernel.org/stable/c/0a59a3895f804469276d188effa511c72e752f35
- https://git.kernel.org/stable/c/193d18f60588e95d62e0f82b6a53893e5f2f19f8
- https://git.kernel.org/stable/c/6e5bff40bb38741e40c33043ba0816fba5f93661
- https://git.kernel.org/stable/c/7b240a8935d554ad36a52c2c37c32039f9afaef2
- https://git.kernel.org/stable/c/88aab153d1528bc559292a12fb5105ee97528e1f
- https://git.kernel.org/stable/c/a21704df4024708be698fb3fd5830d5b113b70e0
- https://git.kernel.org/stable/c/be0974be5c42584e027883ac2af7dab5e950098c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71127.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
