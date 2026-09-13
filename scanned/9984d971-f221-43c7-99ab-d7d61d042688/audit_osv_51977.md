# [M] CVE-2021-46919

## Summary
Severity: Medium
Advisory: CVE-2021-46919
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46919
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: fix wq size store permission state

WQ size can only be changed when the device is disabled. Current code
allows change when device is enabled but wq is disabled. Change the check
to detect device state.

## References
- https://git.kernel.org/stable/c/05b7791c4c4aa8304368fdc55ae911f6b34e7281
- https://git.kernel.org/stable/c/0fff71c5a311e1264988179f7dcc217fda15fadd
- https://git.kernel.org/stable/c/4ecf25595273203010bc8318c4aee60ad64037ae
