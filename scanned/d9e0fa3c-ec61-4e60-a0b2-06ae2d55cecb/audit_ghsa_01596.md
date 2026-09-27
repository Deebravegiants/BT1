# [C] Markdown-supplied Shell Command Execution

## Summary
Severity: Critical
Advisory: GHSA-c84h-w6cr-5v8q
CVE: CVE-2020-15271
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-c84h-w6cr-5v8q
Type: github-advisory

## Affected
- PyPI: `lookatme` — affected >=0 <2.3.0

## Details
### Impact

lookatme versions prior to 2.3.0 automatically loaded the built-in "terminal" and "file_loader" extensions. Users that use lookatme to render untrusted markdown may have malicious shell commands automatically run on their system.

### Patches

Users should upgrade to lookatme versions 2.3.0 or above.

### Workarounds

The `lookatme/contrib/terminal.py` and `lookatme/contrib/file_loader.py` files may be manually deleted. Additionally, it is always recommended to be aware of what is being rendered with lookatme.

### References

* https://github.com/d0c-s4vage/lookatme/pull/110
* https://github.com/d0c-s4vage/lookatme/releases/tag/v2.3.0

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [d0c-s4vage/lookatme](https://github.com/d0c-s4vage/lookatme)

## References
- https://github.com/d0c-s4vage/lookatme/security/advisories/GHSA-c84h-w6cr-5v8q
- https://nvd.nist.gov/vuln/detail/CVE-2020-15271
- https://github.com/d0c-s4vage/lookatme/pull/110
- https://github.com/d0c-s4vage/lookatme/commit/72fe36b784b234548d49dae60b840c37f0eb8d84
- https://github.com/d0c-s4vage/lookatme
- https://github.com/d0c-s4vage/lookatme/releases/tag/v2.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/lookatme/PYSEC-2020-61.yaml
- https://pypi.org/project/lookatme/#history
