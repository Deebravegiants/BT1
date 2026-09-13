# [H] OpenProject: Information Disclosure (cleartext storage of data) on localhost through memcached via Others "storage.<id>.httpx_access_token" leads to Sensitive Data Exposure

## Summary
Severity: High
Advisory: CVE-2026-52783
Aliases: GHSA-h83w-5q5x-pq27
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52783
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.3 and 17.4.1, OpenProject's Storages module writes the OneDrive/SharePoint userless OAuth access_token plaintext to Rails.cache under the deterministic key storage.<id>.httpx_access_token, repopulated continuously by an hourly cron and every userless-OAuth call site (see Write cadence). None of the three allowed cache backends (file_store, memcache, redis) encrypts at rest. An attacker with read access to the cache backend recovers the Azure-AD application-tier bearer with an anonymous get over the memcached binary protocol (or the equivalent against Redis). This vulnerability is fixed in 17.3.3 and 17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52783.json
- https://github.com/opf/openproject/security/advisories/GHSA-h83w-5q5x-pq27
- https://nvd.nist.gov/vuln/detail/CVE-2026-52783
