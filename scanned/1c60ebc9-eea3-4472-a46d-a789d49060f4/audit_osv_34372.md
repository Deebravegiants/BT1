# [M] FreePBX vulnerable to unauthenticated Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2025-59056
Aliases: GHSA-frc2-jhgg-rwpr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/AU:Y/R:U/V:D/RE:L/U:Red)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-59056
Type: osv

## Details
FreePBX is an open-source web-based graphical user interface. In FreePBX 15, 16, and 17, malicious connections to the Administrator Control Panel web interface can cause the uninstall function to be triggered for certain modules. This function drops the module's database tables, which is where most modules store their configuration. This vulnerability is fixed in 15.0.38, 16.0.41, and 17.0.21.

## References
- https://github.com/FreePBX/framework/blame/release/17.0/amp_conf/htdocs/admin/ajax.php#L18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59056.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-frc2-jhgg-rwpr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59056
