# [H] Pickle serialization vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-5m22-cfq9-86x6
CVE: CVE-2023-23930
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-13
Source: https://github.com/advisories/GHSA-5m22-cfq9-86x6
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <4.0.2

## Details
### What
We are using pickle as default serialization module but that has known security issues (see e.g. https://medium.com/ochrona/python-pickle-is-notoriously-insecure-d6651f1974c9). 

In summary, it is not advisable to open Pickles that you create yourself locally. In vantage6, algorithms use pickles to send aggregated data around and to pack algorithm input or output. All of the Python algorithms that use the wrappers with default serialization are therefore vulnerable to this issue.

Solution: we should use JSON instead

### Impact
All users of vantage6 that post tasks with algorithms that use the default serialization. The default serialization is used by default with all algorithm wrappers.

### Patches
Not yet

### Workarounds
Specify JSON serialization

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-5m22-cfq9-86x6
- https://nvd.nist.gov/vuln/detail/CVE-2023-23930
- https://github.com/vantage6/vantage6/commit/e62f03bacf2247bd59eed217e2e7338c3a01a5f0
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6/PYSEC-2023-196.yaml
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/0682c4288f43fee5bcc72dc448cdd99bd7e57f76/docs/release_notes.rst#400
- https://medium.com/ochrona/python-pickle-is-notoriously-insecure-d6651f1974c9
