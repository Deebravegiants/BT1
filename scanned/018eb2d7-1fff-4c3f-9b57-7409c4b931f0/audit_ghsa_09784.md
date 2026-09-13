# [M] uutils coreutils has a Time-of-check Time-of-use (TOCTOU) Race Condition

## Summary
Severity: Medium
Advisory: GHSA-q6m9-xj2w-xmrc
CVE: CVE-2026-35360
CWE: CWE-367
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-q6m9-xj2w-xmrc
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0

## Details
The touch utility in uutils coreutils is vulnerable to a Time-of-Check to Time-of-Use (TOCTOU) race condition during file creation. When the utility identifies a missing path, it later attempts creation using File::create(), which internally uses O_TRUNC. An attacker can exploit this window to create a file or swap a symlink at the target path, causing touch to truncate an existing file and leading to permanent data loss.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35360
- https://github.com/uutils/coreutils/issues/10019
- https://github.com/uutils/coreutils
