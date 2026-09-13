# [M] CVE-2021-47263

## Summary
Severity: Medium
Advisory: CVE-2021-47263
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47263
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: wcd934x: Fix shift-out-of-bounds error

bit-mask for pins 0 to 4 is BIT(0) to BIT(4) however we ended up with BIT(n - 1)
which is not right, and this was caught by below usban check

UBSAN: shift-out-of-bounds in drivers/gpio/gpio-wcd934x.c:34:14

## References
- https://git.kernel.org/stable/c/dbec64b11c65d74f31427e2b9d5746fbf17bf840
- https://git.kernel.org/stable/c/dd55331d493b7ea75c5db1f24d6822946fde2862
- https://git.kernel.org/stable/c/e0b518a2eb44d8a74c19e50f79a8ed393e96d634
