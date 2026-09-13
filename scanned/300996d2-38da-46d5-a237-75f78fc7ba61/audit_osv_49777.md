# [H] CVE-2019-19048

## Summary
Severity: High
Advisory: CVE-2019-19048
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19048
Type: osv

## Details
A memory leak in the crypto_reportstat() function in drivers/virt/vboxguest/vboxguest_utils.c in the Linux kernel before 5.3.9 allows attackers to cause a denial of service (memory consumption) by triggering copy_form_user() failures, aka CID-e0b0cb938864.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4226-1/
- https://github.com/torvalds/linux/commit/e0b0cb9388642c104838fac100a4af32745621e2
