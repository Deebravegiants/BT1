# [M] Net::OAuth versions before 0.32 for Perl allow memory exhaustion via unbounded caching of failed module loads in smart_require

## Summary
Severity: Medium
Advisory: CVE-2026-72888
Aliases: GHSA-m2cv-cq5x-47ph
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-72888
Type: osv

## Details
Net::OAuth versions before 0.32 for Perl allow memory exhaustion via unbounded caching of failed module loads in smart_require.

smart_require stores results in a process-global hash with no bound and no eviction, and keeps an entry for every class name it is asked about, including names that failed to load, because the return value of the failed eval is stored before the error is checked. The key comes off the wire on the server side: _signature_method_class builds the class name from the signature_method parameter of the incoming message, and verify resolves it before any signature is checked.

A remote client chooses both how many entries are created and how long each key is. In a persistent server the hash grows for the life of the worker process until it exhausts memory. Header size limits bound the key length on the Authorization header path, but not on a POST body.

## References
- http://www.openwall.com/lists/oss-security/2026/08/16/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72888.json
- https://github.com/vurtdev/Net-OAuth/security/advisories/GHSA-m2cv-cq5x-47ph
- https://metacpan.org/release/RRWO/Net-OAuth-0.32/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-72888
- https://github.com/vurtdev/Net-OAuth/commit/ee713fc96263c70b3b9a5280612618b474576f8f.patch
- https://github.com/vurtdev/Net-OAuth
