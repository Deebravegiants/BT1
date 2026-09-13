# [C] CVE-2019-11873

## Summary
Severity: Critical
Advisory: CVE-2019-11873
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2019-11873
Type: osv

## Details
wolfSSL 4.0.0 has a Buffer Overflow in DoPreSharedKeys in tls13.c when a current identity size is greater than a client identity size. An attacker sends a crafted hello client packet over the network to a TLSv1.3 wolfSSL server. The length fields of the packet: record length, client hello length, total extensions length, PSK extension length, total identity length, and identity length contain their maximum value which is 2^16. The identity data field of the PSK extension of the packet contains the attack data, to be stored in the undefined memory (RAM) of the server. The size of the data is about 65 kB. Possibly the attacker can perform a remote code execution attack.

## References
- http://www.securityfocus.com/bid/108466
- https://www.telekom.com/en/corporate-responsibility/data-protection-data-security/security/details/advisories-504842
- https://www.telekom.com/resource/blob/572524/1c89c1cbaccdf792153063b3a10af10e/dl-190515-remote-buffer-overflow-vulnerability-wolfssl-library-data.pdf
