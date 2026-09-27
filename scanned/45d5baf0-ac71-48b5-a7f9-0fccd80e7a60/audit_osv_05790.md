# [M] BIT-haproxy-2021-39241

## Summary
Severity: Medium
Advisory: BIT-haproxy-2021-39241
Aliases: CVE-2021-39241
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2021-39241
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.4.0 <2.4.3

## Details
An issue was discovered in HAProxy 2.0 before 2.0.24, 2.2 before 2.2.16, 2.3 before 2.3.13, and 2.4 before 2.4.3. An HTTP method name may contain a space followed by the name of a protected resource. It is possible that a server would interpret this as a request for that protected resource, such as in the "GET /admin? HTTP/1.1 /static/images HTTP/1.1" example.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=89265224d314a056d77d974284802c1b8a0dc97f
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ALECUZDIMT5FYGP6V6PVSI4BKVZTZWN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RPNY4WZIQUAUOCLIMUPC37AQWNXTWIQM/
- https://www.debian.org/security/2021/dsa-4960
- https://www.mail-archive.com/haproxy%40formilux.org/msg41041.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-39241
