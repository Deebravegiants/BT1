# [M] CVE-2021-3418

## Summary
Severity: Medium
Advisory: CVE-2021-3418
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-3418
Type: osv

## Details
If certificates that signed grub are installed into db, grub can be booted directly. It will then boot any kernel without signature validation. The booted kernel will think it was booted in secureboot mode and will implement lockdown, yet it could have been tampered. This flaw is a reintroduction of CVE-2020-15705 and only affects grub2 versions prior to 2.06 and upstream and distributions using the shim_lock mechanism.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1933757
