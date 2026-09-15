# [M] CVE-2018-15919

## Summary
Severity: Medium
Advisory: CVE-2018-15919
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-08-28
Source: https://osv.dev/vulnerability/CVE-2018-15919
Type: osv

## Details
Remotely observable behaviour in auth-gss2.c in OpenSSH through 7.8 could be used by remote attackers to detect existence of users on a target system when GSS2 is in use. NOTE: the discoverer states 'We understand that the OpenSSH developers do not want to treat such a username enumeration (or "oracle") as a vulnerability.'

## References
- http://www.securityfocus.com/bid/105163
- https://security.netapp.com/advisory/ntap-20181221-0001/
- http://seclists.org/oss-sec/2018/q3/180
