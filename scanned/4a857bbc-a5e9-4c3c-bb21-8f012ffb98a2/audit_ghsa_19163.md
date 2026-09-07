# [M] Mautic allows Relative Path Traversal in assets file upload

## Summary
Severity: Medium
Advisory: GHSA-4w2w-36vm-c8hf
CVE: CVE-2022-25773
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-26
Source: https://github.com/advisories/GHSA-4w2w-36vm-c8hf
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <5.2.3

## Details
### Summary

This advisory addresses a file placement vulnerability that could allow assets to be uploaded to unintended directories on the server.

* **Improper Limitation of a Pathname to a Restricted Directory:** A vulnerability exists in the asset upload functionality that allows users to upload files to directories outside of the intended temporary directory.

### Mitigation

Please update to 5.2.3 or later.

### Workarounds

None

### References

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-4w2w-36vm-c8hf
- https://nvd.nist.gov/vuln/detail/CVE-2022-25773
- https://github.com/mautic/mautic/commit/e6aaad99f399c5df1ce6273609920098e5c2564a
- https://github.com/mautic/mautic
