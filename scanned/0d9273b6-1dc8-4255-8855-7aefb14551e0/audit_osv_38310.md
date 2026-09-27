# [H] Path Traversal in kedro-org/kedro

## Summary
Severity: High
Advisory: CVE-2026-3840
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-3840
Type: osv

## Details
A vulnerability in Kedro version 1.2.0 allows an attacker to exploit path traversal by providing a crafted version string. The `_get_versioned_path()` method in `kedro/io/core.py` directly interpolates user-supplied version strings into filesystem paths without sanitization. This enables an attacker to escape the intended versioned dataset directory and access files outside the expected path. The issue is also reachable through the CLI via the `--load-versions` parameter, as `_split_load_versions()` in `kedro/framework/cli/utils.py` does not validate the version string. This vulnerability can lead to unauthorized file reads, data poisoning, cross-project or cross-tenant data access, and broader downstream impacts in environments where Kedro is used with automation or orchestration layers.

## References
- https://huntr.com/bounties/156dead0-1ad5-487f-b7f5-84e707277f76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3840.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3840
