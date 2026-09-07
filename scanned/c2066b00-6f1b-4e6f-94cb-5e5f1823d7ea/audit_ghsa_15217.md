# [M] Minor fix to previous patch for CVE-2022-35918

## Summary
Severity: Medium
Advisory: GHSA-8qw9-gf7w-42x5
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-12
Source: https://github.com/advisories/GHSA-8qw9-gf7w-42x5
Type: github-advisory

## Affected
- PyPI: `streamlit` — affected >=0.63.0 <1.30.0

## Details
### Impact

The initial vulnerability identified in Streamlit apps using custom components, allowing for directory traversal attacks, was addressed in version 1.11.1. However, a minor issue persisted, which could still potentially expose certain files on the server file-system under specific conditions.

### Patches

We released an update in version 1.30.0 to further tighten security measures. Users are strongly advised to update to version 1.30.0 immediately for optimal security.

### Workarounds

No additional workarounds are necessary once the update to version 1.30.0 is applied.

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@streamlit.io](mailto:security@streamlit.io)

## References
- https://github.com/streamlit/streamlit/security/advisories/GHSA-8qw9-gf7w-42x5
- https://github.com/streamlit/streamlit/commit/bd0a8996c4c7ec55b9c6557e7b168b0c13a25b90
- https://github.com/advisories/GHSA-v4hr-4jpx-56gc
- https://github.com/streamlit/streamlit
- https://www.cve.org/CVERecord?id=CVE-2022-35918
