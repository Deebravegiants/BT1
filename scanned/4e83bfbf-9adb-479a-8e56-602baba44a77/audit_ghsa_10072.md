# [H] uutils coreutils has an Untrusted Search Path

## Summary
Severity: High
Advisory: GHSA-mh5c-xrmh-m794
CVE: CVE-2026-35368
CWE: CWE-426
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-mh5c-xrmh-m794
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0

## Details
A vulnerability exists in the chroot utility of uutils coreutils when using the --userspec option. The utility resolves the user specification via getpwnam() after entering the chroot but before dropping root privileges. On glibc-based systems, this can trigger the Name Service Switch (NSS) to load shared libraries (e.g., libnss_*.so.2) from the new root directory. If the NEWROOT is writable by an attacker, they can inject a malicious NSS module to execute arbitrary code as root, facilitating a full container escape or privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35368
- https://github.com/uutils/coreutils/issues/10327
- https://github.com/uutils/coreutils
