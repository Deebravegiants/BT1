# [H] CVE-2021-47241

## Summary
Severity: High
Advisory: CVE-2021-47241
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47241
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: strset: fix message length calculation

Outer nest for ETHTOOL_A_STRSET_STRINGSETS is not accounted for.
This may result in ETHTOOL_MSG_STRSET_GET producing a warning like:

    calculated message payload length (684) not sufficient
    WARNING: CPU: 0 PID: 30967 at net/ethtool/netlink.c:369 ethnl_default_doit+0x87a/0xa20

and a splat.

As usually with such warnings three conditions must be met for the warning
to trigger:
 - there must be no skb size rounding up (e.g. reply_size of 684);
 - string set must be per-device (so that the header gets populated);
 - the device name must be at least 12 characters long.

all in all with current user space it looks like reading priv flags
is the only place this could potentially happen. Or with syzbot :)

## References
- https://git.kernel.org/stable/c/cfc7f0e70d649e6d2233fba0d9390b525677d971
- https://git.kernel.org/stable/c/e175aef902697826d344ce3a12189329848fe898
- https://git.kernel.org/stable/c/fb3a948143688e14e2cfd2a2812877923d0e5e92
