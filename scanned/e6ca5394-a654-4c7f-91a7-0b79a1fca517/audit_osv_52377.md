# [M] CVE-2021-47385

## Summary
Severity: Medium
Advisory: CVE-2021-47385
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47385
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (w83792d) Fix NULL pointer dereference by removing unnecessary structure field

If driver read val value sufficient for
(val & 0x08) && (!(val & 0x80)) && ((val & 0x7) == ((val >> 4) & 0x7))
from device then Null pointer dereference occurs.
(It is possible if tmp = 0b0xyz1xyz, where same literals mean same numbers)
Also lm75[] does not serve a purpose anymore after switching to
devm_i2c_new_dummy_device() in w83791d_detect_subclients().

The patch fixes possible NULL pointer dereference by removing lm75[].

Found by Linux Driver Verification project (linuxtesting.org).

[groeck: Dropped unnecessary continuation lines, fixed multipline alignment]

## References
- https://git.kernel.org/stable/c/24af1fe376e22c42238a4a604d31e46c486876c3
- https://git.kernel.org/stable/c/0f36b88173f028e372668ae040ab1a496834d278
- https://git.kernel.org/stable/c/1499bb2c3a87a2efea0065adab2bd66badee61c3
- https://git.kernel.org/stable/c/200ced5ba724d8bbf29dfac4ed1e17a39ccaccd1
