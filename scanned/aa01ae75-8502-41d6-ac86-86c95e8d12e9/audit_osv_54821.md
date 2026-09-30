# [H] CVE-2024-46304

## Summary
Severity: High
Advisory: CVE-2024-46304
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-46304
Type: osv

## Details
A NULL pointer dereference in libcoap v4.3.5-rc2 and below allows a remote attacker to cause a denial of service via the coap_handle_request_put_block function in src/coap_block.c.

## References
- https://github.com/obgm/libcoap/issues/1509
