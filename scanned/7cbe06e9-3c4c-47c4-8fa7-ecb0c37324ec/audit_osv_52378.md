# [H] CVE-2021-47386

## Summary
Severity: High
Advisory: CVE-2021-47386
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47386
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (w83791d) Fix NULL pointer dereference by removing unnecessary structure field

If driver read val value sufficient for
(val & 0x08) && (!(val & 0x80)) && ((val & 0x7) == ((val >> 4) & 0x7))
from device then Null pointer dereference occurs.
(It is possible if tmp = 0b0xyz1xyz, where same literals mean same numbers)
Also lm75[] does not serve a purpose anymore after switching to
devm_i2c_new_dummy_device() in w83791d_detect_subclients().

The patch fixes possible NULL pointer dereference by removing lm75[].

Found by Linux Driver Verification project (linuxtesting.org).

[groeck: Dropped unnecessary continuation lines, fixed multi-line alignment]

## References
- https://git.kernel.org/stable/c/516d9055039017a20a698103be2b556b4c976bb8
- https://git.kernel.org/stable/c/943c15ac1b84d378da26bba41c83c67e16499ac4
- https://git.kernel.org/stable/c/16887ae4e3defd2c4e7913b6c539f33eaf4eac5c
- https://git.kernel.org/stable/c/44d3c480e4e2a75bf6296a18b4356157991ccd80
