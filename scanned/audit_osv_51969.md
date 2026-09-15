# [M] CVE-2021-46911

## Summary
Severity: Medium
Advisory: CVE-2021-46911
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46911
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ch_ktls: Fix kernel panic

Taking page refcount is not ideal and causes kernel panic
sometimes. It's better to take tx_ctx lock for the complete
skb transmit, to avoid page cleanup if ACK received in middle.

## References
- https://git.kernel.org/stable/c/1a73e427b824133940c2dd95ebe26b6dce1cbf10
- https://git.kernel.org/stable/c/8348665d4181c68b0ca1205b48e1753d78bc810f
- https://git.kernel.org/stable/c/8d5a9dbd2116a852f8f0f91f6fbc42a0afe1091f
