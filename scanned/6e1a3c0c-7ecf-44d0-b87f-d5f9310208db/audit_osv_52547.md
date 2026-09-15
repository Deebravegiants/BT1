# [H] CVE-2021-47565

## Summary
Severity: High
Advisory: CVE-2021-47565
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47565
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpt3sas: Fix kernel panic during drive powercycle test

While looping over shost's sdev list it is possible that one
of the drives is getting removed and its sas_target object is
freed but its sdev object remains intact.

Consequently, a kernel panic can occur while the driver is trying to access
the sas_address field of sas_target object without also checking the
sas_target object for NULL.

## References
- https://git.kernel.org/stable/c/5d4d50b1f159a5ebab7617f47121b4370aa58afe
- https://git.kernel.org/stable/c/7e324f734a914957b8cc3ff4b4c9f0409558adb5
- https://git.kernel.org/stable/c/8485649a7655e791a6e4e9f15b4d30fdae937184
- https://git.kernel.org/stable/c/dd035ca0e7a142870a970d46b1d19276cfe2bc8c
- https://git.kernel.org/stable/c/0d4b29eaadc1f59cec0c7e85eae77d08fcca9824
- https://git.kernel.org/stable/c/0ee4ba13e09c9d9c1cb6abb59da8295d9952328b
- https://git.kernel.org/stable/c/2bf9c5a5039c8f4b037236aed505e6a25c1d5f7b
- https://git.kernel.org/stable/c/58ef2c7a6de13721865d84b80eecf56d6cba0937
