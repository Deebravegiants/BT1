# [H] CVE-2023-2828

## Summary
Severity: High
Advisory: CVE-2023-2828
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-21
Source: https://osv.dev/vulnerability/CVE-2023-2828
Type: osv

## Details
Every `named` instance configured to run as a recursive resolver maintains a cache database holding the responses to the queries it has recently sent to authoritative servers. The size limit for that cache database can be configured using the `max-cache-size` statement in the configuration file; it defaults to 90% of the total amount of memory available on the host. When the size of the cache reaches 7/8 of the configured limit, a cache-cleaning algorithm starts to remove expired and/or least-recently used RRsets from the cache, to keep memory use below the configured limit.

It has been discovered that the effectiveness of the cache-cleaning algorithm used in `named` can be severely diminished by querying the resolver for specific RRsets in a certain order, effectively allowing the configured `max-cache-size` limit to be significantly exceeded.
This issue affects BIND 9 versions 9.11.0 through 9.16.41, 9.18.0 through 9.18.15, 9.19.0 through 9.19.13, 9.11.3-S1 through 9.16.41-S1, and 9.18.11-S1 through 9.18.15-S1.

## References
- https://kb.isc.org/docs/cve-2023-2828
- https://lists.debian.org/debian-lts-announce/2023/07/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SEFCEVCTYEMKTWA7V7EYPI5YQQ4JWDLI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U3K6AJK7RRSR53HRF5GGKPA6PDUDWOD2/
- https://security.netapp.com/advisory/ntap-20230703-0010/
- https://www.debian.org/security/2023/dsa-5439
- http://www.openwall.com/lists/oss-security/2023/06/21/6
