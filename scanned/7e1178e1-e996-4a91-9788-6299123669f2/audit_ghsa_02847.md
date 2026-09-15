# [M] Client metadata path-traversal

## Summary
Severity: Medium
Advisory: GHSA-wjw6-2cqr-j4qr
CVE: CVE-2021-41131
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-wjw6-2cqr-j4qr
Type: github-advisory

## Affected
- PyPI: `tuf` — affected >=0 <0.19.0

## Details
### Impact
In both clients (`tuf/client` and `tuf/ngclient`), there is a path traversal vulnerability that in the worst case can overwrite files ending in `.json` anywhere on the client system on a call to `get_one_valid_targetinfo()`. It occurs because the rolename is used to form the filename, and may contain path traversal characters (ie `../../name.json`).

The impact is mitigated by a few facts:
* It only affects implementations that allow arbitrary rolename selection for delegated targets metadata
* The attack requires the ability to A) insert new metadata for the path-traversing role and B) get the role delegated by an existing targets metadata
* The written file content is heavily restricted since it needs to be a valid, signed targets file. The file extension is always .json.

### Patches
A fix is available in version 0.19 or newer.

### Workarounds
None that do not require code changes. Clients can restrict the allowed character set for rolenames, or they can store metadata in files named in a way that is not vulnerable: neither of these approaches is possible without modifying python-tuf.

### References
- [The issue where this was discovered](https://github.com/theupdateframework/python-tuf/issues/1527)
- [Proof of Concept demonstrating the flaw](https://github.com/jku/path-traversal-poc)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [python-tuf](https://github.com/theupdateframework/python-tuf/issues)
* Contact the maintainers by email or Slack

## References
- https://github.com/theupdateframework/python-tuf/security/advisories/GHSA-wjw6-2cqr-j4qr
- https://nvd.nist.gov/vuln/detail/CVE-2021-41131
- https://github.com/theupdateframework/python-tuf/issues/1527
- https://github.com/theupdateframework/python-tuf/commit/4ad7ae48fda594b640139c3b7eae21ed5155a102
- https://github.com/pypa/advisory-database/tree/main/vulns/tuf/PYSEC-2021-376.yaml
- https://github.com/theupdateframework/python-tuf
