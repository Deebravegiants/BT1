# [H] 3X-UI Vulnerable to Authenticated Arbitrary File Write via Database Import and Xray Log Path Manipulation

## Summary
Severity: High
Advisory: GHSA-jm48-m3rr-9hgg
CVE: CVE-2026-55477
CWE: CWE-20, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-jm48-m3rr-9hgg
Type: github-advisory

## Affected
- Go: `github.com/mhsanaei/3x-ui/v3` — affected >=0 <3.3.1
- Go: `github.com/mhsanaei/3x-ui/v2` — affected >=0

## Details
# Summary

An authenticated administrator can abuse the database import functionality to achieve arbitrary file write on the host by modifying Xray configuration values stored in the database. This can be leveraged to obtain code execution and persistent access as the user running Xray (including root when Xray is running as root).

# Details

The database import functionality trusts attacker-controlled configuration values without sufficient validation.

An authenticated administrator can export the SQLite database, modify `xrayTemplateConfig.log.access` to point to an arbitrary file, and import the modified database back into the panel. The attacker can then inject controlled content into an inbound client's `email` field. When a connection is processed, Xray writes the attacker-controlled content to the configured access log path.

Because the log path is fully attacker-controlled, this behavior results in arbitrary file write as the user running Xray. Depending on the target file and service privileges, this can be used to obtain code execution and persistent host access.

# PoC

1. Authenticate as a panel administrator.
2. Export the panel database.
3. Modify `xrayTemplateConfig.log.access` to point to a writable target file (e.g. `~/.ssh/authorized_keys`).
4. Inject an attacker-controlled SSH public key into an inbound client's `email` field.
5. Import the modified database.
6. Trigger a connection through the modified inbound.
7. Xray writes the attacker-controlled content to the specified file, allowing SSH access as the user running Xray.

A complete PoC is available and can be provided privately.

# Impact

Type: Authenticated Arbitrary File Write -> Privilege Escalation / Code Execution

Any authenticated 3X-UI administrator can write attacker-controlled content to arbitrary files accessible by the Xray process. This allows compromise of the account running Xray and may lead to full host compromise depending on deployment configuration and service privileges.

In environments where Xray runs as root, successful exploitation results in persistent root access.

# Patches

Fixed in **v3.3.1**.

`resolveXrayLogPaths` (`internal/web/service/xray.go`) now confines the Xray `log.access` and `log.error` paths to the panel's log folder: any configured value is reduced to its base filename under `config.GetLogFolder()`. Absolute paths (such as `/etc/cron.d/...` or `~/.ssh/authorized_keys`) and `..` traversal can no longer make Xray write outside the log folder, while `""` and `"none"` continue to disable logging. The confinement is applied during Xray configuration generation, so it covers every way the template can be set — the database import and the built-in raw Xray configuration editor alike.

# Workarounds

None other than upgrading. Until you can update to v3.3.1, restrict panel administrator access to fully trusted operators.

# Notes

The underlying issue is the unrestricted log path rather than the database import alone: an administrator can set the same `xrayTemplateConfig.log.access` / `log.error` value directly through the built-in raw Xray configuration editor, which is why the fix hardens the value at configuration-generation time to cover every vector. The client `email` field is also independently validated (control characters, spaces, and slashes are rejected), which constrains what can be written into a log line; the reliable primitive is therefore arbitrary file write (creation, append, or corruption) at an attacker-chosen path, with code execution dependent on a suitable writable target and the privileges of the Xray process.

## References
- https://github.com/MHSanaei/3x-ui/security/advisories/GHSA-jm48-m3rr-9hgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55477
- https://github.com/MHSanaei/3x-ui/commit/80e168787ed608e83a065033ee94c8bfc3025ce7
- https://github.com/MHSanaei/3x-ui
- https://github.com/MHSanaei/3x-ui/releases/tag/v3.3.1
