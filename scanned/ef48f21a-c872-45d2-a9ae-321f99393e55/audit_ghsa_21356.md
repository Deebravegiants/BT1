# [H] melisplatform/melis-asset-manager vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-7fj2-rrq6-rphq
CVE: CVE-2022-39296
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-7fj2-rrq6-rphq
Type: github-advisory

## Affected
- Packagist: `melisplatform/melis-asset-manager` — affected >=0 <5.0.1

## Details
### Impact

Attackers can read arbitrary files on affected versions of `melisplatform/melis-asset-manager`, leading to the disclosure of sensitive information. Conducting this attack does not require authentication.

Users should immediately upgrade to `melisplatform/melis-asset-manager` >= 5.0.1.

### Patches

This issue was addressed by restricting access to files to intended directories only.

### References

- https://github.com/melisplatform/melis-asset-manager/commit/a0f75918c049aff78953a0bc91c585153595d1bd

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/melisplatform/melis-asset-manager/security/advisories/GHSA-7fj2-rrq6-rphq
- https://nvd.nist.gov/vuln/detail/CVE-2022-39296
- https://github.com/melisplatform/melis-asset-manager/commit/a0f75918c049aff78953a0bc91c585153595d1bd
- https://github.com/melisplatform/melis-asset-manager
