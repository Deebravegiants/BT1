# [M] BIT-haproxy-2024-53008

## Summary
Severity: Medium
Advisory: BIT-haproxy-2024-53008
Aliases: CVE-2024-53008
Ecosystem: Bitnami
Published: 2024-12-05
Source: https://osv.dev/vulnerability/BIT-haproxy-2024-53008
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.0.0 <3.0.3

## Details
Inconsistent interpretation of HTTP requests ('HTTP Request/Response Smuggling') issue exists in HAProxy. If this vulnerability is exploited,  a remote attacker may access a path that is restricted by ACL (Access Control List) set on the product. As a result, the attacker may obtain sensitive information.

## References
- https://git.haproxy.org/?p=haproxy-2.6.git;a=commit;h=1afca10150ac3e4e2224055cc31b6f1e4a70efe2
- https://git.haproxy.org/?p=haproxy-2.8.git;a=commit;h=01c1056a44823c5ffb8f74660b32c099d9b5355b
- https://git.haproxy.org/?p=haproxy-2.9.git;a=commit;h=4bcaece344c8738dac1ab5bd8cc81e2a22701d71
- https://git.haproxy.org/?p=haproxy-3.0.git;a=commit;h=95a607c4b3af09be2a495b9c2872ea252ccff603
- https://jvn.jp/en/jp/JVN88385716/
- https://www.haproxy.org/
- https://nvd.nist.gov/vuln/detail/CVE-2024-53008
