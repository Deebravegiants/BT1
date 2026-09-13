# [M] CVE-2019-10129

## Summary
Severity: Medium
Advisory: CVE-2019-10129
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10129
Type: osv

## Details
A vulnerability was found in postgresql versions 11.x prior to 11.3. Using a purpose-crafted insert to a partitioned table, an attacker can read arbitrary bytes of server memory. In the default configuration, any user can create a partitioned table suitable for this attack. (Exploit prerequisites are the same as for CVE-2018-1052).

## References
- https://security.gentoo.org/glsa/202003-03
- https://www.postgresql.org/about/news/1939/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10129
