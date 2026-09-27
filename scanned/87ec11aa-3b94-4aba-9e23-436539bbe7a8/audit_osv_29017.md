# [M] CVE-2024-38808: Spring Expression DoS Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-38808
Aliases: GHSA-9cmq-m9j5-mvww
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-38808
Type: osv

## Details
In Spring Framework versions 5.3.0 - 5.3.38 and older unsupported versions, it is possible for a user to provide a specially crafted Spring Expression Language (SpEL) expression that may cause a denial of service (DoS) condition.

Specifically, an application is vulnerable when the following is true:

  *  The application evaluates user-supplied SpEL expressions.

## References
- https://spring.io/security/cve-2024-38808
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38808.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38808
- https://security.netapp.com/advisory/ntap-20240920-0002/
