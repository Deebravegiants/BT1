# [H] CVE-2021-31826

## Summary
Severity: High
Advisory: CVE-2021-31826
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-27
Source: https://osv.dev/vulnerability/CVE-2021-31826
Type: osv

## Details
Shibboleth Service Provider 3.x before 3.2.2 is prone to a NULL pointer dereference flaw involving the session recovery feature. The flaw is exploitable (for a daemon crash) on systems not using this feature if a crafted cookie is supplied.

## References
- https://git.shibboleth.net/view/?p=cpp-sp.git%3Ba=commit%3Bh=5a47c3b9378f4c49392dd4d15189b70956f9f2ec
- https://shibboleth.net/community/advisories/secadv_20210426.txt
- https://www.debian.org/security/2021/dsa-4905
- https://bugs.debian.org/987608
- https://issues.shibboleth.net/jira/browse/SSPCPP-927
