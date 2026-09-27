# [H] BIT-haproxy-2023-25950

## Summary
Severity: High
Advisory: BIT-haproxy-2023-25950
Aliases: CVE-2023-25950
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2023-25950
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.7.0 <2.7.1

## Details
HTTP request/response smuggling vulnerability in HAProxy version 2.7.0, and 2.6.1 to 2.6.7 allows a remote attacker to alter a legitimate user's request. As a result, the attacker may obtain sensitive information or cause a denial-of-service (DoS) condition.

## References
- https://git.haproxy.org/?p=haproxy-2.7.git%3Ba=commit%3Bh=3ca4223c5e1f18a19dc93b0b09ffdbd295554d46
- https://jvn.jp/en/jp/JVN38170084/
- https://www.haproxy.org/
- https://nvd.nist.gov/vuln/detail/CVE-2023-25950
