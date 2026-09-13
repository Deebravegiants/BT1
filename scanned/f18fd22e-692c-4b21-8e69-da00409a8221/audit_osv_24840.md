# [H] CVE-2023-27538

## Summary
Severity: High
Advisory: CVE-2023-27538
Aliases: CURL-CVE-2023-27538
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-27538
Type: osv

## Details
An authentication bypass vulnerability exists in libcurl prior to v8.0.0 where it reuses a previously established SSH connection despite the fact that an SSH option was modified, which should have prevented reuse. libcurl maintains a pool of previously used connections to reuse them for subsequent transfers if the configurations match. However, two SSH settings were omitted from the configuration check, allowing them to match easily, potentially leading to the reuse of an inappropriate connection.

## References
- https://hackerone.com/reports/1898475
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27538.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27538
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0010/
- https://lists.debian.org/debian-lts-announce/2023/04/msg00025.html
