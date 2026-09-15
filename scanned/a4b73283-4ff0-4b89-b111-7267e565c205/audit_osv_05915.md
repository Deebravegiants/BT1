# [C] BIT-java-2024-40896

## Summary
Severity: Critical
Advisory: BIT-java-2024-40896
Aliases: BIT-java-min-2024-40896, BIT-jre-2024-40896, CVE-2024-40896
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-40896
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

## Details
In libxml2 2.11 before 2.11.9, 2.12 before 2.12.9, and 2.13 before 2.13.3, the SAX parser can produce events for external entities even if custom SAX handlers try to override entity content (by setting "checked"). This makes classic XXE attacks possible.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/1a8932303969907f6572b1b6aac4081c56adb5c6
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/761
- https://nvd.nist.gov/vuln/detail/CVE-2024-40896
- https://security.netapp.com/advisory/ntap-20250228-0004/
