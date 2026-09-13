# [M] BIT-haproxy-2025-32464

## Summary
Severity: Medium
Advisory: BIT-haproxy-2025-32464
Aliases: CVE-2025-32464
Ecosystem: Bitnami
Published: 2025-04-11
Source: https://osv.dev/vulnerability/BIT-haproxy-2025-32464
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.0.0 <3.1.7

## Details
HAProxy 2.2 through 3.1.6, in certain uncommon configurations, has a sample_conv_regsub heap-based buffer overflow because of mishandling of the replacement of multiple short patterns with a longer one.

## References
- https://github.com/haproxy/haproxy/commit/3e3b9eebf871510aee36c3a3336faac2f38c9559
- https://nvd.nist.gov/vuln/detail/CVE-2025-32464
- https://lists.debian.org/debian-lts-announce/2025/04/msg00031.html
