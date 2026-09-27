# [H] CVE-2023-30362

## Summary
Severity: High
Advisory: CVE-2023-30362
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-30362
Type: osv

## Details
Buffer Overflow vulnerability in coap_send function in libcoap library 4.3.1-103-g52cfd56 fixed in 4.3.1-120-ge242200 allows attackers to obtain sensitive information via malformed pdu.

## References
- https://github.com/obgm/libcoap/issues/1063
- https://github.com/obgm/libcoap/pull/1065
