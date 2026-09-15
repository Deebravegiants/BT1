# [M] CVE-2021-47070

## Summary
Severity: Medium
Advisory: CVE-2021-47070
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47070
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

uio_hv_generic: Fix another memory leak in error handling paths

Memory allocated by 'vmbus_alloc_ring()' at the beginning of the probe
function is never freed in the error handling path.

Add the missing 'vmbus_free_ring()' call.

Note that it is already freed in the .remove function.

## References
- https://git.kernel.org/stable/c/261bbd90cc53d2835343f056770156cf1e82cf03
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/0b0226be3a52dadd965644bc52a807961c2c26df
- https://git.kernel.org/stable/c/5f59240cf25b2f7a0fdffc2701482a70310fec07
