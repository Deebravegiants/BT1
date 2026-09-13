# [M] CVE-2021-46949

## Summary
Severity: Medium
Advisory: CVE-2021-46949
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46949
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: farch: fix TX queue lookup in TX flush done handling

We're starting from a TXQ instance number ('qid'), not a TXQ type, so
 efx_get_tx_queue() is inappropriate (and could return NULL, leading
 to panics).

## References
- https://git.kernel.org/stable/c/a1570985ec04116cc665b760faf666a104154170
- https://git.kernel.org/stable/c/fb791572d6747ef385f628450f8d57cd132e6e5a
- https://git.kernel.org/stable/c/5b1faa92289b53cad654123ed2bc8e10f6ddd4ac
- https://git.kernel.org/stable/c/98d91180748986bfb6dfb3e72765f3225719a647
