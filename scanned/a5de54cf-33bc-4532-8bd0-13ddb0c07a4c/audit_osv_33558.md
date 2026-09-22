# [M] FreshRSS vulnerable to favicon cache poisoning via proxy

## Summary
Severity: Medium
Advisory: CVE-2025-46339
Aliases: GHSA-8f79-3q3w-43c4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-46339
Type: osv

## Details
FreshRSS is a self-hosted RSS feed aggregator. Prior to version 1.26.2, it's possible to poison feed favicons by adding a given URL as a feed with the proxy set to an attacker-controlled one and disabled SSL verifying. The favicon hash is computed by hashing the feed URL and the salt, whilst not including the following variables: proxy address, proxy protocol, and whether SSL should be verified. Therefore it's possible to poison a favicon of a given feed by simply intercepting the response of the feed, and changing the website URL to one where a threat actor controls the feed favicon. Feed favicons can be replaced for all users by anyone. Version 1.26.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46339.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-8f79-3q3w-43c4
- https://nvd.nist.gov/vuln/detail/CVE-2025-46339
- https://github.com/FreshRSS/FreshRSS/commit/3776e1e48f33e80eb4b674bb64b419caf3b5a4e2
