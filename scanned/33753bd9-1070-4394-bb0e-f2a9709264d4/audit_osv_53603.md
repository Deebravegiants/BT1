# [M] CVE-2023-0469

## Summary
Severity: Medium
Advisory: CVE-2023-0469
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2023-0469
Type: osv

## Details
A use-after-free flaw was found in io_uring/filetable.c in io_install_fixed_file in the io_uring subcomponent in the Linux Kernel during call cleanup. This flaw may lead to a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2163723
