# [H] theshit vulnerable to unsafe loading of user-owned Python rules when running as root

## Summary
Severity: High
Advisory: GHSA-95qg-89c2-w5hj
CVE: CVE-2025-69257
CWE: CWE-269
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-95qg-89c2-w5hj
Type: github-advisory

## Affected
- crates.io: `theshit` — affected >=0 <0.1.1

## Details
### Impact

**Vulnerability Type:** Local Privilege Escalation (LPE) / Arbitrary Code Execution.

The application loads custom Python rules and configuration files from user-writable locations (e.g., `~/.config/theshit/`) without validating ownership or permissions when executed with elevated privileges.

If the tool is invoked with `sudo` or otherwise runs with an effective UID of root, it continues to trust configuration files originating from the unprivileged user's environment. This allows a local attacker to inject arbitrary Python code via a malicious rule or configuration file, which is then executed with root privileges.

**Who is impacted:**
Any system where this tool is executed with elevated privileges is affected. In environments where the tool is permitted to run via `sudo` without a password (`NOPASSWD`), a local unprivileged user can escalate privileges to root without additional interaction.

### Patches

The issue has been fixed in version **0.1.1**.

The patch introduces strict ownership and permission checks for all configuration files and custom rules. The application now enforces that rules are only loaded if they are owned by the effective user executing the tool.

When executed with elevated privileges (`EUID=0`), the application refuses to load any files that are not owned by root or that are writable by non-root users. When executed as a non-root user, it similarly refuses to load rules owned by other users. This prevents both vertical and horizontal privilege escalation via execution of untrusted code.

### Workarounds

If upgrading is not possible, users should avoid executing the pplication with `sudo` or as the root user.

As a temporary mitigation, ensure that directories containing custom rules and configuration files are owned by root and are not writable by non-root users. Administrators may also audit existing custom rules before running the tool with elevated privileges.

### References

* [Commit fixing the issue](https://github.com/AsfhtgkDavid/theshit/commit/3dc12905cafb5fd47fff4071a05c231f925ac113)
* CWE-269: Improper Privilege Management
* CWE-284: Improper Access Control
* CWE-829: Inclusion of Functionality from Untrusted Control Sphere

## References
- https://github.com/AsfhtgkDavid/theshit/security/advisories/GHSA-95qg-89c2-w5hj
- https://nvd.nist.gov/vuln/detail/CVE-2025-69257
- https://github.com/AsfhtgkDavid/theshit/commit/8e0b565e7876a83b0e1cfbacb8af39dadfdcc500
- https://github.com/AsfhtgkDavid/theshit
- https://rustsec.org/advisories/RUSTSEC-2025-0139.html
