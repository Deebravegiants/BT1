# [H] BIT-haproxy-2021-39240

## Summary
Severity: High
Advisory: BIT-haproxy-2021-39240
Aliases: CVE-2021-39240
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2021-39240
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.4.0 <2.4.3

## Details
An issue was discovered in HAProxy 2.2 before 2.2.16, 2.3 before 2.3.13, and 2.4 before 2.4.3. It does not ensure that the scheme and path portions of a URI have the expected characters. For example, the authority field (as observed on a target HTTP/2 server) might differ from what the routing rules were intended to achieve.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=4b8852c70d8c4b7e225e24eb58258a15eb54c26e
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=a495e0d94876c9d39763db319f609351907a31e8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ALECUZDIMT5FYGP6V6PVSI4BKVZTZWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RPNY4WZIQUAUOCLIMUPC37AQWNXTWIQM/
- https://www.debian.org/security/2021/dsa-4960
- https://www.mail-archive.com/haproxy%40formilux.org/msg41041.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-39240
