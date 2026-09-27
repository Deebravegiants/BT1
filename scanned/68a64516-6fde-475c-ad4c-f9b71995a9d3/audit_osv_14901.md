# [H] CVE-2019-12312

## Summary
Severity: High
Advisory: CVE-2019-12312
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/CVE-2019-12312
Type: osv

## Details
In Libreswan 3.27 an assertion failure can lead to a pluto IKE daemon restart. An attacker can trigger a NULL pointer dereference by initiating an IKEv2 IKE_SA_INIT exchange, followed by a bogus INFORMATIONAL exchange instead of the normallly expected IKE_AUTH exchange. This affects send_v2N_spi_response_from_state() in programs/pluto/ikev2_send.c that will then trigger a NULL pointer dereference leading to a restart of libreswan.

## References
- https://libreswan.org/security/CVE-2019-12312/CVE-2019-12312.txt
- https://libreswan.org/security/CVE-2019-12312/libreswan-3.27-CVE-2019-12312.patch
- https://github.com/libreswan/libreswan/issues/246
- https://github.com/libreswan/libreswan/compare/9b1394e...3897683
- http://www.iwantacve.cn/index.php/archives/218/
