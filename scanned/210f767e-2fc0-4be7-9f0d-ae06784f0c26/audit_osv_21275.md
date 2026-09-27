# [H] CVE-2021-41611

## Summary
Severity: High
Advisory: CVE-2021-41611
Aliases: GHSA-47m4-g3mv-9q5r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-41611
Type: osv

## Details
An issue was discovered in Squid 5.0.6 through 5.1.x before 5.2. When validating an origin server or peer certificate, Squid may incorrectly classify certain certificates as trusted. This problem allows a remote server to obtain security trust well improperly. This indication of trust may be passed along to clients, allowing access to unsafe or hijacked services.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CWQ2WKDWTSO47S3F6XJJ6HGG2ULWEAE4/
- http://www.openwall.com/lists/oss-security/2021/12/23/2
- http://www.squid-cache.org/Versions/v6/changesets/squid-6-43d6b5c81b88ec2256b430c69a872a1e4f324e4a.patch
- https://github.com/squid-cache/squid/security/advisories/GHSA-47m4-g3mv-9q5r
