# [M] CVE-2023-29465

## Summary
Severity: Medium
Advisory: CVE-2023-29465
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-06
Source: https://osv.dev/vulnerability/CVE-2023-29465
Type: osv

## Details
SageMath FlintQS 1.0 relies on pathnames under TMPDIR (typically world-writable), which (for example) allows a local user to overwrite files with the privileges of a different user (who is running FlintQS).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29465.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29465
- https://github.com/sagemath/FlintQS/issues/3
- https://github.com/sagemath/sage/pull/35419
