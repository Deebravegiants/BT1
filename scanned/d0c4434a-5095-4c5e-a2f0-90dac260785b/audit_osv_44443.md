# [M] Robots::Validate versions from 0.3.2 before 0.3.11 for Perl allow unbounded outbound DNS queries per validation via a forward-confirmation loop that does not bound the names it queries

## Summary
Severity: Medium
Advisory: CVE-2026-82309
Aliases: GHSA-6399-5qhh-48h5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-82309
Type: osv

## Details
Robots::Validate versions from 0.3.2 before 0.3.11 for Perl allow unbounded outbound DNS queries per validation via a forward-confirmation loop that does not bound the names it queries.

_check_dns issues one PTR query for the client address, keeps the returned names matching the rule's domain, and issues a forward query for each until one resolves back to that address. Nothing bounds that list, and a client controls the reverse zone for its own address, so it chooses how many names the PTR answer holds. Net::DNS refetches a truncated answer over TCP by default, so the 512-byte UDP payload does not cap it either.

Any client whose User-Agent matches a rule with a domain reaches _check_dns. Each forward name is distinct and client-chosen, so every query misses the local cache and is resolved against the authoritative servers for that domain. The queries are synchronous, so the caller is held until all of them answer or time out.

## References
- http://www.openwall.com/lists/oss-security/2026/09/04/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82309.json
- https://github.com/robrwo/Robots-Validate/security/advisories/GHSA-6399-5qhh-48h5
- https://metacpan.org/release/RRWO/Robots-Validate-v0.4.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-82309
- https://github.com/robrwo/Robots-Validate/commit/6426178c49ff6c440922f31a92a6feb3c661b143.patch
- https://github.com/robrwo/Robots-Validate
