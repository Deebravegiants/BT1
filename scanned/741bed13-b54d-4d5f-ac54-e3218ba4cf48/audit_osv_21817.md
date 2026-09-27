# [M] CVE-2021-46784

## Summary
Severity: Medium
Advisory: CVE-2021-46784
Aliases: GHSA-f5cp-6rh3-284w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-17
Source: https://osv.dev/vulnerability/CVE-2021-46784
Type: osv

## Details
In Squid 3.x through 3.5.28, 4.x through 4.17, and 5.x before 5.6, due to improper buffer management, a Denial of Service can occur when processing long Gopher server responses.

## References
- http://www.openwall.com/lists/oss-security/2023/10/13/1
- http://www.openwall.com/lists/oss-security/2023/10/13/10
- http://www.openwall.com/lists/oss-security/2023/10/21/1
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2021_7.patch
- https://security-tracker.debian.org/tracker/CVE-2021-46784
- https://security.netapp.com/advisory/ntap-20221223-0007/
- http://www.squid-cache.org/Versions/v5/changesets/SQUID-2021_7.patch
- https://github.com/squid-cache/squid/commit/5e2ea2b13bd98f53e29964ca26bb0d602a8a12b9
- https://github.com/squid-cache/squid/security/advisories/GHSA-f5cp-6rh3-284w
