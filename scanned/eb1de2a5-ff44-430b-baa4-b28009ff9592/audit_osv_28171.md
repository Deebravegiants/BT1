# [H] Unrestricted upload and download paths in check_sftp

## Summary
Severity: High
Advisory: CVE-2024-28826
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-28826
Type: osv

## Details
Improper restriction of local upload and download paths in check_sftp in Checkmk before 2.3.0p4, 2.2.0p27, 2.1.0p44, and in Checkmk 2.0.0 (EOL) allows attackers with sufficient permissions to configure the check to read and write local files on the Checkmk site server.

## References
- https://checkmk.com/werk/15200
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28826.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28826
