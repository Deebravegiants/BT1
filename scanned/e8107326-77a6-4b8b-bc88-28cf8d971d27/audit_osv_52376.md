# [M] CVE-2021-47384

## Summary
Severity: Medium
Advisory: CVE-2021-47384
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47384
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (w83793) Fix NULL pointer dereference by removing unnecessary structure field

If driver read tmp value sufficient for
(tmp & 0x08) && (!(tmp & 0x80)) && ((tmp & 0x7) == ((tmp >> 4) & 0x7))
from device then Null pointer dereference occurs.
(It is possible if tmp = 0b0xyz1xyz, where same literals mean same numbers)
Also lm75[] does not serve a purpose anymore after switching to
devm_i2c_new_dummy_device() in w83791d_detect_subclients().

The patch fixes possible NULL pointer dereference by removing lm75[].

Found by Linux Driver Verification project (linuxtesting.org).

[groeck: Dropped unnecessary continuation lines, fixed multi-line alignments]

## References
- https://git.kernel.org/stable/c/6cb01fe630eaffc5a2c3f7364436caddba286623
- https://git.kernel.org/stable/c/746011193f44f97f8784edcf8327c587946745fc
- https://git.kernel.org/stable/c/7c4fd5de39f273626a2b0f3a446d2cc85cd47616
- https://git.kernel.org/stable/c/dd4d747ef05addab887dc8ff0d6ab9860bbcd783
