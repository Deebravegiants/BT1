# [M] CVE-2023-25399

## Summary
Severity: Medium
Advisory: CVE-2023-25399
Aliases: GHSA-9jx5-6pgf-crrp, PYSEC-2023-102
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-25399
Type: osv

## Details
A refcounting issue which leads to potential memory leak was discovered in scipy commit 8627df31ab in Py_FindObjects() function. Note: This is disputed as a bug and not a vulnerability. SciPy is not designed to be exposed to untrusted users or data directly.

## References
- http://www.square16.org/achievement/cve-2023-25399/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25399.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25399
- https://github.com/scipy/scipy/issues/16235
- https://github.com/scipy/scipy/issues/16235#issuecomment-1625361328
- https://github.com/scipy/scipy/pull/16397
