# [M] Tendenci has Authenticated Remote Code Execution via Pickle Deserialization

## Summary
Severity: Medium
Advisory: CVE-2026-23946
Aliases: GHSA-339m-4qw5-j2g3, PYSEC-2026-1950
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-23946
Type: osv

## Details
Tendenci is an open source content management system built for non-profits, associations and cause-based sites. Versions 15.3.11 and below include a critical deserialization vulnerability in the Helpdesk module (which is not enabled by default). This vulnerability allows Remote Code Execution (RCE) by an authenticated user with staff security level due to using Python's pickle module in helpdesk /reports/. The original CVE-2020-14942 was incompletely patched. While ticket_list() was fixed to use safe JSON deserialization, the run_report() function still uses unsafe pickle.loads(). The impact is limited to the permissions of the user running the application, typically www-data, which generally lacks write (except for upload directories) and execute permissions. This issue has been fixed in version 15.3.12.

## References
- https://docs.python.org/3/library/pickle.html#restricting-globals
- https://github.com/tendenci/tendenci/releases/tag/v15.3.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23946.json
- https://github.com/advisories/GHSA-jqmc-fxxp-r589
- https://github.com/tendenci/tendenci/security/advisories/GHSA-339m-4qw5-j2g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-23946
- https://github.com/tendenci/tendenci/issues/867
- https://github.com/tendenci/tendenci/commit/23d9fd85ab7654e9c83cfc86cb4175c0bd7a77f1
- https://github.com/tendenci/tendenci/commit/2ff0a457614944a1b417081c543ea4c5bb95d636
- https://github.com/tendenci/tendenci/commit/63e1b84a5b163466d1d8d811d35e7021a7ca0d0e
