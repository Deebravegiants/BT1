# [M] uutils coreutils doesn't properly handle setuid and setgid bits when ownership preservation fails

## Summary
Severity: Medium
Advisory: GHSA-x2wv-9p67-mh9w
CVE: CVE-2026-35350
CWE: CWE-281
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-x2wv-9p67-mh9w
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0

## Details
The cp utility in uutils coreutils fails to properly handle setuid and setgid bits when ownership preservation fails. When copying with the -p (preserve) flag, the utility applies the source mode bits even if the chown operation is unsuccessful. This can result in a user-owned copy retaining original privileged bits, creating unexpected privileged executables that violate local security policies. This differs from GNU cp, which clears these bits when ownership cannot be preserved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35350
- https://github.com/uutils/coreutils/issues/9750
- https://github.com/uutils/coreutils
