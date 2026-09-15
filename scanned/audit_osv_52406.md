# [M] CVE-2021-47415

## Summary
Severity: Medium
Advisory: CVE-2021-47415
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47415
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iwlwifi: mvm: Fix possible NULL dereference

In __iwl_mvm_remove_time_event() check that 'te_data->vif' is NULL
before dereferencing it.

## References
- https://git.kernel.org/stable/c/24d5f16e407b75bc59d5419b957a9cab423b2681
- https://git.kernel.org/stable/c/432d8185e9ffce97e3866ca71c39b0807a456920
