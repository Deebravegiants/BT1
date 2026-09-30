# [M] CVE-2021-47211

## Summary
Severity: Medium
Advisory: CVE-2021-47211
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47211
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: fix null pointer dereference on pointer cs_desc

The pointer cs_desc return from snd_usb_find_clock_source could
be null, so there is a potential null pointer dereference issue.
Fix this by adding a null check before dereference.

## References
- https://git.kernel.org/stable/c/58fa50de595f152900594c28ec9915c169643739
- https://git.kernel.org/stable/c/b97053df0f04747c3c1e021ecbe99db675342954
