# [M] CVE-2021-46948

## Summary
Severity: Medium
Advisory: CVE-2021-46948
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46948
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: farch: fix TX queue lookup in TX event handling

We're starting from a TXQ label, not a TXQ type, so
 efx_channel_get_tx_queue() is inappropriate (and could return NULL,
 leading to panics).

## References
- https://git.kernel.org/stable/c/35c7a83ad1bb1d48ae249346e61b1132bcbf9052
- https://git.kernel.org/stable/c/83b09a1807415608b387c7bc748d329fefc5617e
- https://git.kernel.org/stable/c/bf2b941d0a6f2d3b9f5fa3c4c21bdd54f71ce253
- https://git.kernel.org/stable/c/e531db1ea6f98c9612cb2de093a107c7eadfb96c
