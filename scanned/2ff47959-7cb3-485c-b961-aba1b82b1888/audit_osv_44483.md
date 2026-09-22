# [M] Path traversal in AshAdmin file uploads via unsanitized client filename

## Summary
Severity: Medium
Advisory: CVE-2026-82673
Aliases: EEF-CVE-2026-82673, GHSA-483p-rgcq-p5j9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82673
Type: osv

## Details
Improper Limitation of a Pathname to a Restricted Directory (Path Traversal) vulnerability in ash-project ash_admin allows writing attacker-controlled bytes to arbitrary paths on the server.

AshAdmin.Components.Resource.Form.consume_file_uploads/1 builds the destination as Path.join([tmp_dir, entry.client_name]) and writes it with File.cp!/2. entry.client_name is the browser-supplied filename and is not sanitized, and Path.join/1 does not normalize ... An upload named ../../../../var/www/app/priv/static/x.png therefore escapes the random temp directory and lands anywhere the BEAM user can write, enabling arbitrary file write and potentially remote code execution by overwriting application assets, configuration, or cron/ssh files. The only guard is an extension allowlist defaulting to :any that checks only the extension. The fix strips path components with Path.basename/1 before joining.

This issue affects ash_admin: from 0.13.7 before 1.3.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82673.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82673
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82673.json
- https://github.com/ash-project/ash_admin/security/advisories/GHSA-483p-rgcq-p5j9
- https://nvd.nist.gov/vuln/detail/CVE-2026-82673
- https://github.com/ash-project/ash_admin/commit/4bb41cb697f3d9be58462d727aed75aba76efc82
- https://github.com/ash-project/ash_admin
