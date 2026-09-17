# [M] Keras: DiskIOStore permits path traversal through crafted layer names

## Summary
Severity: Medium
Advisory: GHSA-gh82-f9x8-5frx
CVE: CVE-2026-12479
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-gh82-f9x8-5frx
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.3
- PyPI: `keras` — affected >=3.13.0 <3.15.0

## Details
A path traversal vulnerability exists in keras-team/keras version 3.14.0, specifically in the `DiskIOStore.make` method within the Keras 3 model saving and loading library. This vulnerability arises from the improper handling of user-provided layer names, which are used to construct directory paths without sanitizing for parent directory components (`..`). While forward slashes (`/`) are restricted in layer names, directory traversal sequences are not. This allows an attacker to craft a malicious Keras model that, when saved or loaded, can escape the intended temporary working directory and perform unauthorized file system operations, such as creating directories or writing files in arbitrary locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12479
- https://github.com/keras-team/keras/pull/23017
- https://github.com/keras-team/keras/commit/d8caeb58cc9e61ea092445dc7a20908ca8d693e2
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.3
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/188836b9-12fc-49c7-8dbf-04f60fe33743
