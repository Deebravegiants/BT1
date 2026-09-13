# [H] CVE-2021-47609

## Summary
Severity: High
Advisory: CVE-2021-47609
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47609
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scpi: Fix string overflow in SCPI genpd driver

Without the bound checks for scpi_pd->name, it could result in the buffer
overflow when copying the SCPI device name from the corresponding device
tree node as the name string is set at maximum size of 30.

Let us fix it by using devm_kasprintf so that the string buffer is
allocated dynamically.

## References
- https://git.kernel.org/stable/c/976389cbb16cee46847e5d06250a3a0b5506781e
- https://git.kernel.org/stable/c/f0f484714f35d24ffa0ecb4afe3df1c5b225411d
- https://git.kernel.org/stable/c/4694b1ec425a2d20d6f8ca3db594829fdf5f2672
- https://git.kernel.org/stable/c/639901b9429a3195e0fead981ed74b51f5f31538
- https://git.kernel.org/stable/c/7e8645ca2c0046f7cd2f0f7d569fc036c8abaedb
- https://git.kernel.org/stable/c/802a1a8501563714a5fe8824f4ed27fec04a0719
- https://git.kernel.org/stable/c/865ed67ab955428b9aa771d8b4f1e4fb7fd08945
