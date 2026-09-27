# [H] BIT-apache-2025-3891

## Summary
Severity: High
Advisory: BIT-apache-2025-3891
Aliases: CVE-2025-3891, GHSA-x7cf-8wgv-5j86
Ecosystem: Bitnami
Published: 2025-05-13
Source: https://osv.dev/vulnerability/BIT-apache-2025-3891
Type: osv

## Affected
- Bitnami: `apache` — affected unspecified

## Details
A flaw was found in the mod_auth_openidc module for Apache httpd. This flaw allows a remote, unauthenticated attacker to trigger a denial of service by sending an empty POST request when the OIDCPreservePost directive is enabled. The server crashes consistently, affecting availability.

## References
- https://access.redhat.com/errata/RHSA-2025:4597
- https://access.redhat.com/security/cve/CVE-2025-3891
- https://bugzilla.redhat.com/show_bug.cgi?id=2361633
- https://lists.debian.org/debian-lts-announce/2025/05/msg00007.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-3891
