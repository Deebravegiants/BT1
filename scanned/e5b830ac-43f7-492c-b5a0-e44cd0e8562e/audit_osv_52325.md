# [M] CVE-2021-47331

## Summary
Severity: Medium
Advisory: CVE-2021-47331
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47331
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: common: usb-conn-gpio: fix NULL pointer dereference of charger

When power on system with OTG cable, IDDIG's interrupt arises before
the charger registration, it will cause a NULL pointer dereference,
fix the issue by registering the power supply before requesting
IDDIG/VBUS irq.

## References
- https://git.kernel.org/stable/c/880287910b1892ed2cb38977893b947382a09d21
- https://git.kernel.org/stable/c/8e8d910e9a3a7fba86140aff4924c30955ab228b
- https://git.kernel.org/stable/c/1a133a0996d6b4c83509d570ed4edcba34c44f25
- https://git.kernel.org/stable/c/436906fd248e018403bcda61a9311d9af02912f1
