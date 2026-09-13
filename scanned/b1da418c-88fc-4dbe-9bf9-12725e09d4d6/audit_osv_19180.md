# [H] CVE-2020-8517

## Summary
Severity: High
Advisory: CVE-2020-8517
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2020-8517
Type: osv

## Details
An issue was discovered in Squid before 4.10. Due to incorrect input validation, the NTLM authentication credentials parser in ext_lm_group_acl may write to memory outside the credentials buffer. On systems with memory access protections, this can result in the helper process being terminated unexpectedly. This leads to the Squid process also terminating and a denial of service for all clients using the proxy.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00018.html
- http://www.squid-cache.org/Advisories/SQUID-2020_3.txt
- https://security.gentoo.org/glsa/202003-34
- https://security.netapp.com/advisory/ntap-20210304-0002/
- https://usn.ubuntu.com/4289-1/
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-6982f1187a26557e582172965e266f544ea562a5.patch
