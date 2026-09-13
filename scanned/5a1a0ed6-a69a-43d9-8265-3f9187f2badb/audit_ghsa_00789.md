# [C] Incorrect threshold signature computation in TUF

## Summary
Severity: Critical
Advisory: GHSA-pwqf-9h7j-7mv8
CVE: CVE-2020-6174
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-21
Source: https://github.com/advisories/GHSA-pwqf-9h7j-7mv8
Type: github-advisory

## Affected
- PyPI: `tuf` — affected >=0 <0.12.2

## Details
### Impact
Metadadata signature verification, as used in `tuf.client.updater`, counted each of multiple signatures with identical authorized keyids  separately towards the threshold. Therefore, an attacker with access to a valid signing key could create multiple valid signatures in order to meet the minimum threshold of keys before the metadata was considered valid.

The tuf maintainers would like to thank Erik MacLean of Analog Devices, Inc. for reporting this issue.

### Patches
A [fix](https://github.com/theupdateframework/tuf/pull/974) is available in version [0.12.2](https://github.com/theupdateframework/tuf/releases/tag/v0.12.2) or newer.

### Workarounds
No workarounds are known for this issue.

### References
* [CVE-2020-6174](https://nvd.nist.gov/vuln/detail/CVE-2020-6174)
* Pull request resolving the issue [PR 974](https://github.com/theupdateframework/tuf/pull/974)

## References
- https://github.com/theupdateframework/tuf/security/advisories/GHSA-pwqf-9h7j-7mv8
- https://nvd.nist.gov/vuln/detail/CVE-2020-6174
- https://github.com/theupdateframework/tuf/pull/974
- https://github.com/theupdateframework/python-tuf/commit/2977188139d065ff3356c3cb4aec60c582b57e0e
- https://github.com/pypa/advisory-database/tree/main/vulns/tuf/PYSEC-2020-147.yaml
- https://github.com/theupdateframework/tuf
- https://github.com/theupdateframework/tuf/releases/tag/v0.12.2
