# [M] CVE-2021-47329

## Summary
Severity: Medium
Advisory: CVE-2021-47329
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47329
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: megaraid_sas: Fix resource leak in case of probe failure

The driver doesn't clean up all the allocated resources properly when
scsi_add_host(), megasas_start_aen() function fails during the PCI device
probe.

Clean up all those resources.

## References
- https://git.kernel.org/stable/c/e623f79691c5104317669ab36ec316a90c05062f
- https://git.kernel.org/stable/c/04b6b9ea80906e3b41ff120b45db31768947cf72
- https://git.kernel.org/stable/c/0680db6f41920b2c91c7df3cc9cd5968701a6f74
- https://git.kernel.org/stable/c/0c6226601c3e191a44a57d8f9f814b7e5c308959
- https://git.kernel.org/stable/c/b5438f48fdd8e1c3f130d32637511efd32038152
