# [H] SysmonElixir path traversal in /read endpoint allows arbitrary file read

## Summary
Severity: High
Advisory: CVE-2025-52574
Aliases: GHSA-9vj4-rv7q-36qj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52574
Type: osv

## Details
SysmonElixir is a system monitor HTTP service in Elixir. Prior to version 1.0.1, the /read endpoint reads any file from the server's /etc/passwd by default. In v1.0.1, a whitelist was added that limits reading to only files under priv/data. This issue has been patched in version 1.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52574.json
- https://github.com/bocaletto-luca/elixir-system-monitor/security/advisories/GHSA-9vj4-rv7q-36qj
- https://nvd.nist.gov/vuln/detail/CVE-2025-52574
- https://github.com/bocaletto-luca/elixir-system-monitor/commit/647a5525f6667a28f1133985213dd080ea11bb87
