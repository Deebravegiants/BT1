# [H] CVE-2019-17185

## Summary
Severity: High
Advisory: CVE-2019-17185
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-21
Source: https://osv.dev/vulnerability/CVE-2019-17185
Type: osv

## Details
In FreeRADIUS 3.0.x before 3.0.20, the EAP-pwd module used a global OpenSSL BN_CTX instance to handle all handshakes. This mean multiple threads use the same BN_CTX instance concurrently, resulting in crashes when concurrent EAP-pwd handshakes are initiated. This can be abused by an adversary as a Denial-of-Service (DoS) attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00039.html
- https://freeradius.org/security/
- https://github.com/FreeRADIUS/freeradius-server/releases/tag/release_3_0_20
