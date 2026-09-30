# [H] CVE-2020-14058

## Summary
Severity: High
Advisory: CVE-2020-14058
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-14058
Type: osv

## Details
An issue was discovered in Squid before 4.12 and 5.x before 5.0.3. Due to use of a potentially dangerous function, Squid and the default certificate validation helper are vulnerable to a Denial of Service when opening a TLS connection to an attacker-controlled server for HTTPS. This occurs because unrecognized error values are mapped to NULL, but later code expects that each error value is mapped to a valid error string.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3RG5FGSTCAYVIJPJHIY3MRZ7NFT6HDO7/
- http://www.squid-cache.org/Advisories/SQUID-2020_6.txt
- https://security.netapp.com/advisory/ntap-20210312-0001/
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-93f5fda134a2a010b84ffedbe833d670e63ba4be.patch
- http://www.squid-cache.org/Versions/v5/changesets/squid-5-c6d1a4f6a2cbebceebc8a3fcd8f539ceb7b7f723.patch
