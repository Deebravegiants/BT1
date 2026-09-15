# [H] BIT-haproxy-2021-39242

## Summary
Severity: High
Advisory: BIT-haproxy-2021-39242
Aliases: CVE-2021-39242
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2021-39242
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.4.0 <2.4.3

## Details
An issue was discovered in HAProxy 2.2 before 2.2.16, 2.3 before 2.3.13, and 2.4 before 2.4.3. It can lead to a situation with an attacker-controlled HTTP Host header, because a mismatch between Host and authority is mishandled.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=b5d2b9e154d78e4075db163826c5e0f6d31b2ab1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ALECUZDIMT5FYGP6V6PVSI4BKVZTZWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RPNY4WZIQUAUOCLIMUPC37AQWNXTWIQM/
- https://www.debian.org/security/2021/dsa-4960
- https://www.mail-archive.com/haproxy%40formilux.org/msg41041.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-39242
