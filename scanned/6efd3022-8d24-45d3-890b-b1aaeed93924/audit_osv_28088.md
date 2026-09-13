# [H] Bluetooth: hci_event: Fix handling of HCI_EV_IO_CAPA_REQUEST

## Summary
Severity: High
Advisory: CVE-2024-27416
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27416
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.309, >=4.20.0 <5.4.271, >=5.5.0 <5.10.212, >=5.11.0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.21, >=6.6.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: Fix handling of HCI_EV_IO_CAPA_REQUEST

If we received HCI_EV_IO_CAPA_REQUEST while
HCI_OP_READ_REMOTE_EXT_FEATURES is yet to be responded assume the remote
does support SSP since otherwise this event shouldn't be generated.

## References
- https://git.kernel.org/stable/c/30a5e812f78e3d1cced90e1ed750bf027599205f
- https://git.kernel.org/stable/c/79820a7e1e057120c49be07cbe10643d0706b259
- https://git.kernel.org/stable/c/7e74aa53a68bf60f6019bd5d9a9a1406ec4d4865
- https://git.kernel.org/stable/c/8e2758cc25891d2b76717aaf89b40ed215de188c
- https://git.kernel.org/stable/c/afec8f772296dd8e5a2a6f83bbf99db1b9ca877f
- https://git.kernel.org/stable/c/c3df637266df29edee85e94cab5fd7041e5753ba
- https://git.kernel.org/stable/c/df193568d61234c81de7ed4d540c01975de60277
- https://git.kernel.org/stable/c/fba268ac36ab19f9763ff90d276cde0ce6cd5f31
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27416.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27416
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
