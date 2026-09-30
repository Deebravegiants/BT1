# [M] Arbitrary system path lookup in h20

## Summary
Severity: Medium
Advisory: GHSA-x234-r5fg-x52m
CVE: CVE-2024-5550
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-x234-r5fg-x52m
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=0

## Details
In h2oai/h2o-3 version 3.40.0.4, an exposure of sensitive information vulnerability exists due to an arbitrary system path lookup feature. This vulnerability allows any remote user to view full paths in the entire file system where h2o-3 is hosted. Specifically, the issue resides in the Typeahead API call, which when requested with a typeahead lookup of '/', exposes the root filesystem including directories such as /home, /usr, /bin, among others. This vulnerability could allow attackers to explore the entire filesystem, and when combined with a Local File Inclusion (LFI) vulnerability, could make exploitation of the server trivial.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5550
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/e76372c2-39be-4984-a7c8-7048a75a25dc
