# [H] Security issue with external entity loading in XML without enabling it

## Summary
Severity: High
Advisory: BIT-libphp-2023-3823
Aliases: BIT-php-2023-3823, BIT-php-min-2023-3823, CVE-2023-3823, GHSA-3qrf-m4j2-pcrr
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2023-3823
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.9

## Details
In PHP versions 8.0.* before 8.0.30, 8.1.* before 8.1.22, and 8.2.* before 8.2.8 various XML functions rely on libxml global state to track configuration variables, like whether external entities are loaded. This state is assumed to be unchanged unless the user explicitly changes it by calling appropriate function. However, since the state is process-global, other modules - such as ImageMagick - may also use this library within the same process, and change that global state for their internal purposes, and leave it in a state where external entities loading is enabled. This can lead to the situation where external XML is parsed with external entities loaded, which can lead to disclosure of any local files accessible to PHP. This vulnerable state may persist in the same process across many requests, until the process is shut down.

## References
- https://github.com/php/php-src/security/advisories/GHSA-3qrf-m4j2-pcrr
- https://lists.debian.org/debian-lts-announce/2023/09/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7NBF77WN6DTVTY2RE73IGPYD6M4PIAWA/
- https://nvd.nist.gov/vuln/detail/CVE-2023-3823
- https://security.netapp.com/advisory/ntap-20230825-0001/
