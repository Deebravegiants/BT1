# [M] CVE-2021-47233

## Summary
Severity: Medium
Advisory: CVE-2021-47233
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47233
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: rt4801: Fix NULL pointer dereference if priv->enable_gpios is NULL

devm_gpiod_get_array_optional may return NULL if no GPIO was assigned.

## References
- https://git.kernel.org/stable/c/ba8a26a7ce8617f9f3d6230de34b2302df086b41
- https://git.kernel.org/stable/c/cb2381cbecb81a8893b2d1e1af29bc2e5531df27
- https://git.kernel.org/stable/c/dc68f0c9e4a001e02376fe87f4bdcacadb27e8a1
