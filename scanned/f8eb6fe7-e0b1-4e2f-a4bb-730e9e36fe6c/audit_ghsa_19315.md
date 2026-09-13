# [M] multicast in source builds from vulnerable setuptools dependency

## Summary
Severity: Medium
Advisory: GHSA-94v7-wxj6-r2q5
CWE: CWE-1395
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-94v7-wxj6-r2q5
Type: github-advisory

## Affected
- PyPI: `multicast` — affected >=0 <2.0.9a0

## Details
### Impact
 * Some source-builds may be impacted by a CWE-1395 (eg. vulnerable `setuptools` dependency).
   * Multicast prior to v2.0.9a3 on systems with minimal dependancies installed may use `setuptools <78.1.1` and thus rely on a compromised dependency. In some cases there is a chance that source-builds would fail due to an exploit of the closely related CVE-2025-47273, or become arbitrarily modified.

### Patches
 * Pre-release version v2.0.9a0 and later resolve the issue by bumping requirements to `setuptools>=80.4`
   * Pre-release version v2.0.9a3 and later are recommended for improved stability over v2.0.9a0

### Workarounds
 * Further hardening in v2.0.9a4+ of the build process in CI builds allowing source builds to be verified via GH attestations.

### References
* [GHSA-5rjg-fvgr-3xxf](https://github.com/pypa/setuptools/security/advisories/GHSA-5rjg-fvgr-3xxf)
* pypa/setuptools#4946

### Fixes
* https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/tests/requirements.txt#L32
* https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/docs/requirements.txt#L27
* https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/requirements.txt#L26
* https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/pyproject.toml#L2

## References
- https://github.com/pypa/setuptools/security/advisories/GHSA-5rjg-fvgr-3xxf
- https://github.com/reactive-firewall/multicast/security/advisories/GHSA-94v7-wxj6-r2q5
- https://github.com/pypa/setuptools/issues/4946
- https://github.com/reactive-firewall/multicast/commit/c5c7c7de272421d944beca8452871bca6bfd151f
- https://github.com/reactive-firewall/multicast
- https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/docs/requirements.txt#L27
- https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/pyproject.toml#L2
- https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/requirements.txt#L26
- https://github.com/reactive-firewall/multicast/blob/c5c7c7de272421d944beca8452871bca6bfd151f/tests/requirements.txt#L32
