# [M] CVE-2021-47022

## Summary
Severity: Medium
Advisory: CVE-2021-47022
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47022
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7615: fix memleak when mt7615_unregister_device()

mt7615_tx_token_put() should get call before mt76_free_pending_txwi().

## References
- https://git.kernel.org/stable/c/107bcbb219ac84d885ac63b25246f8d33212bc47
- https://git.kernel.org/stable/c/4fa28c807da54c1d720b3cc12e48eb9bea1e2c8f
- https://git.kernel.org/stable/c/6c5b2b0c6e5a6ce2d8f9f85b8b72bfad60eaa506
- https://git.kernel.org/stable/c/8ab31da7b89f71c4c2defcca989fab7b42f87d71
