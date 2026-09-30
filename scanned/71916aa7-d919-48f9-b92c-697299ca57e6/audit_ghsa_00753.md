# [M] HTTP Request Smuggling in Waitress: Invalid whitespace characters in headers (Follow-up)

## Summary
Severity: Medium
Advisory: GHSA-968f-66r5-5v74
CVE: CVE-2019-16789
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2020-01-06
Source: https://github.com/advisories/GHSA-968f-66r5-5v74
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=0 <1.4.2

## Details
### Impact

The patches introduced to fix https://github.com/Pylons/waitress/security/advisories/GHSA-m5ff-3wj3-8ph4 were not complete and still would allow an attacker to smuggle requests/split a HTTP request with invalid data.

This updates the existing CVE with ID: CVE-2019-16789

### Patches

Waitress version 1.4.2 has been updated to now validate HTTP headers better to avoid the issue, completely fixing all known issues with whitespace.

### Workarounds

There are no work-arounds, upgrading to Waitress 1.4.2 is highly recommended.

### References

See https://github.com/Pylons/waitress/security/advisories/GHSA-m5ff-3wj3-8ph4 for more information on the security issue.

### For more information

If you have any questions or comments about this advisory:

* open an issue at https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: pylons-project-security@googlegroups.com (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-968f-66r5-5v74
- https://nvd.nist.gov/vuln/detail/CVE-2019-16789
- https://github.com/github/advisory-review/pull/14604
- https://github.com/Pylons/waitress/commit/11d9e138125ad46e951027184b13242a3c1de017
- https://github.com/Pylons/waitress/commit/ddb65b489d01d696afa1695b75fdd5df3e4ffdf8
- https://access.redhat.com/errata/RHSA-2020:0720
- https://docs.pylonsproject.org/projects/waitress/en/latest/#security-fixes
- https://github.com/Pylons/waitress
- https://github.com/advisories/GHSA-968f-66r5-5v74
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2019-138.yaml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GVDHR2DNKCNQ7YQXISJ45NT4IQDX3LJ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYEOTGWJZVKPRXX2HBNVIYWCX73QYPM5
- https://www.oracle.com/security-alerts/cpuapr2022.html
