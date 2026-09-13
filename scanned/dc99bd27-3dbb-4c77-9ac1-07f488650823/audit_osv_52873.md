# [H] CVE-2022-1949

## Summary
Severity: High
Advisory: CVE-2022-1949
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-1949
Type: osv

## Details
An access control bypass vulnerability found in 389-ds-base. That mishandling of the filter that would yield incorrect results, but as that has progressed, can be determined that it actually is an access control bypass. This may allow any remote unauthenticated user to issue a filter that allows searching for database items they do not have access to, including but not limited to potentially userPassword hashes and other sensitive data.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2091781
