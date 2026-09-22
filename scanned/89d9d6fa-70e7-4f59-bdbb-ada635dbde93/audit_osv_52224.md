# [M] CVE-2021-47215

## Summary
Severity: Medium
Advisory: CVE-2021-47215
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47215
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: kTLS, Fix crash in RX resync flow

For the TLS RX resync flow, we maintain a list of TLS contexts
that require some attention, to communicate their resync information
to the HW.
Here we fix list corruptions, by protecting the entries against
movements coming from resync_handle_seq_match(), until their resync
handling in napi is fully completed.

## References
- https://git.kernel.org/stable/c/cc4a9cc03faa6d8db1a6954bb536f2c1e63bdff6
- https://git.kernel.org/stable/c/ebeda7a9528ae690e6bf12791a868f0cca8391f2
