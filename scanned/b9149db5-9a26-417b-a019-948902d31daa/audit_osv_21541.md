# [M] CVE-2021-43820

## Summary
Severity: Medium
Advisory: CVE-2021-43820
Aliases: GHSA-m3wc-jv6r-hvv8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-43820
Type: osv

## Details
Seafile is an open source cloud storage system. A sync token is used in Seafile file syncing protocol to authorize access to library data. To improve performance, the token is cached in memory in seaf-server. Upon receiving a token from sync client or SeaDrive client, the server checks whether the token exist in the cache. However, if the token exists in cache, the server doesn't check whether it's associated with the specific library in the URL. This vulnerability makes it possible to use any valid sync token to access data from any **known** library. Note that the attacker has to first find out the ID of a library which it has no access to. The library ID is a random UUID, which is not possible to be guessed. There are no workarounds for this issue.

## References
- https://github.com/haiwen/seafile-server/security/advisories/GHSA-m3wc-jv6r-hvv8
- https://github.com/haiwen/seafile-server/pull/520
