# [H] theshit's Improper Privilege Dropping Allows Local Privilege Escalation via Command Re-execution

## Summary
Severity: High
Advisory: GHSA-2j3p-gqw5-g59j
CVE: CVE-2026-21882
CWE: CWE-250, CWE-269, CWE-273
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-2j3p-gqw5-g59j
Type: github-advisory

## Affected
- crates.io: `theshit` — affected >=0 <0.2.0

## Details
### Impact

**Vulnerability Type:** Local Privilege Escalation (LPE) / Improper Privilege Management / Arbitrary Command Execution.

The application automatically re-executes the previously failed command but does not properly drop elevated privileges during this process.

When the tool is executed with `sudo` or otherwise runs with an effective UID of root, it records the last executed command and attempts to rerun it. However, the application fails to restore the original unprivileged user context before re-executing the command. As a result, the retried command is executed with root privileges, even if the original command was issued by an unprivileged user.

This allows a local attacker to intentionally trigger a failed command under elevated execution and gain arbitrary command execution as root via the retry mechanism.

**Who is impacted:**
Any system where this tool is executed with elevated privileges is affected. The risk is especially high in environments where the tool is permitted to run via `sudo`, including configurations with `NOPASSWD`, as an unprivileged user can escalate privileges to root without additional interaction.

### Proof of Concept

To verify the vulnerability without a shell, attempt to create a file in a root-protected directory.

**1. Verify the file does not exist**
```bash
sudo ls /root/proof_of_lpe
# Output: No such file or directory
```

**2. Run the vulnerable command**
```bash
sudo bash -c "SH_PREV_CMD='touch /root/proof_of_lpe' target/release/theshit fix"
```

**3. Check if the file was created by root**
```bash
sudo ls -l /root/proof_of_lpe
```

**Expected Result:**
The command succeeds silently, and the file `/root/proof_of_lpe` is created, confirming arbitrary command execution with root privileges.

### Patches

The issue has been fixed in version **0.1.2**.

The patch ensures that privilege levels are correctly handled during command re-execution. Before retrying any previously executed command, the application now explicitly resets the effective UID and GID to the original invoking user.

### Workarounds

If upgrading is not possible, users should avoid executing the application with `sudo` or as the root user.

As a temporary mitigation, administrators should restrict the use of the tool in privileged contexts and ensure it is not included in `sudoers` configurations, particularly with `NOPASSWD`. Running the tool strictly as an unprivileged user prevents exploitation of the retry mechanism.

### References

* [Commit fixing the issue](https://github.com/AsfhtgkDavid/theshit/commit/5293957b119e55212dce2c6dcbaf1d7eb794602a)
* CWE-269: Improper Privilege Management
* CWE-273: Improper Check for Dropped Privileges
* CWE-250: Execution with Unnecessary Privileges

## References
- https://github.com/AsfhtgkDavid/theshit/security/advisories/GHSA-2j3p-gqw5-g59j
- https://nvd.nist.gov/vuln/detail/CVE-2026-21882
- https://github.com/AsfhtgkDavid/theshit/commit/5293957b119e55212dce2c6dcbaf1d7eb794602a
- https://github.com/AsfhtgkDavid/theshit
