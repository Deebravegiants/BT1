# [M] Client Denial of Service on TUF

## Summary
Severity: Medium
Advisory: GHSA-2828-9vh6-9m6j
CVE: CVE-2020-6173
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-08-21
Source: https://github.com/advisories/GHSA-2828-9vh6-9m6j
Type: github-advisory

## Affected
- PyPI: `tuf` — affected >=0.7.2 <0.12.2

## Details
### Impact
An attacker who can gain file access to the repository and modify metadata files may cause a denial of service to clients by creating many invalid signatures on a metadata file. Having a large number of signatures to verify will delay the moment when the client will determine the signature is not valid. This delay may be for at least a few minutes, but possibly could be longer especially if multiple files are impacted.

The tuf maintainers would like to thank Erik MacLean of Analog Devices, Inc. for reporting this issue.

### Patches
No fix exists for this issue. 

### Workarounds
No workarounds are known for this issue.

### References
* [CVE-2020-6173](https://nvd.nist.gov/vuln/detail/CVE-2020-6173)
* [Issue #973](https://github.com/theupdateframework/tuf/issues/973)

## References
- https://github.com/theupdateframework/tuf/security/advisories/GHSA-2828-9vh6-9m6j
- https://nvd.nist.gov/vuln/detail/CVE-2020-6173
- https://github.com/theupdateframework/tuf/issues/973
- https://github.com/pypa/advisory-database/tree/main/vulns/tuf/PYSEC-2020-146.yaml
- https://github.com/theupdateframework/tuf
- https://github.com/theupdateframework/tuf/commits/develop
