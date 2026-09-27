# [M] CVE-2021-47437

## Summary
Severity: Medium
Advisory: CVE-2021-47437
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47437
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adis16475: fix deadlock on frequency set

With commit 39c024b51b560
("iio: adis16475: improve sync scale mode handling"), two deadlocks were
introduced:
 1) The call to 'adis_write_reg_16()' was not changed to it's unlocked
    version.
 2) The lock was not being released on the success path of the function.

This change fixes both these issues.

## References
- https://git.kernel.org/stable/c/04e03b907022ebd876f422f17efcc2c6cc934dc6
- https://git.kernel.org/stable/c/9da1b86865ab4376408c58cd9fec332c8bdb5c73
