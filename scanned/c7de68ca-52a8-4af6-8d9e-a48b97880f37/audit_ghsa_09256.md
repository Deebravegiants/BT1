# [H]  pgAdmin 4 File Manager has symbolic-link path traversal

## Summary
Severity: High
Advisory: GHSA-hr4r-fwpv-c95j
CVE: CVE-2026-7819
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hr4r-fwpv-c95j
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
Symbolic-link path traversal (CWE-61, CWE-22) in pgAdmin 4 File Manager.

check_access_permission used os.path.abspath, which resolves '..' but does not resolve symbolic links, while the subsequent kernel write follows symlinks. An authenticated user could plant a symbolic link inside their own storage directory pointing outside it and induce pgAdmin to write to any path reachable by the pgAdmin process.

Fix switches the access check to os.path.realpath for both source and destination, and adds an _open_upload_target helper that opens the target with O_NOFOLLOW (mode 0o600) to close the leaf-component TOCTOU between the access check and the open. File mode is hardened from 0o644 to 0o600.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7819
- https://github.com/pgadmin-org/pgadmin4/issues/9902
- https://github.com/pgadmin-org/pgadmin4/commit/435752b83
- https://github.com/pgadmin-org/pgadmin4
