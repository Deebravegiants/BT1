# [M] Defining resource name as integer may give unintended access in vantage6

## Summary
Severity: Medium
Advisory: GHSA-7x94-6g2m-3hp2
CVE: CVE-2023-28635
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-13
Source: https://github.com/advisories/GHSA-7x94-6g2m-3hp2
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <4.0.0

## Details
### Impact
Malicious users may try to get access to resources they are not allowed to see, by creating resources with integers as names.

One example where this is a risk, is when users define which users are allowed to run algorithms on their node. This may be defined by username or user id. Now, for example, if user id 13 is allowed to run tasks, and an attacker creates a username with username '13', they would be wrongly allowed to run an algorithm.

There may also be other places in the code where such a mixup of resource ID or name leads to issues. The best solution we see is therefore to check when resources are created or modified, that the resource name always starts with a character.

### Patches
To be done, probably in v3.9

### Workarounds
None

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-7x94-6g2m-3hp2
- https://nvd.nist.gov/vuln/detail/CVE-2023-28635
- https://github.com/vantage6/vantage6/pull/744
- https://github.com/vantage6/vantage6/commit/aacfc24548cbf168579d2e13b2ddaf8ded715d36
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6-node/PYSEC-2023-198.yaml
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/0682c4288f43fee5bcc72dc448cdd99bd7e57f76/docs/release_notes.rst#400
