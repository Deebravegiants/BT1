# [H] CVE-2020-10650

## Summary
Severity: High
Advisory: CVE-2020-10650
Aliases: GHSA-rpr3-cw39-3pxh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-26
Source: https://osv.dev/vulnerability/CVE-2020-10650
Type: osv

## Details
A deserialization flaw was discovered in jackson-databind through 2.9.10.4. It could allow an unauthenticated user to perform code execution via ignite-jta or quartz-core: org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup, org.apache.ignite.cache.jta.jndi.CacheJndiTmFactory, and org.quartz.utils.JNDIConnectionProvider.

## References
- https://github.com/advisories/GHSA-rpr3-cw39-3pxh
- https://lists.debian.org/debian-lts-announce/2023/04/msg00032.html
- https://security.netapp.com/advisory/ntap-20230818-0007/
- https://github.com/FasterXML/jackson-databind/commit/a424c038ba0c0d65e579e22001dec925902ac0ef
- https://github.com/FasterXML/jackson-databind/issues/2658
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2022.html
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
