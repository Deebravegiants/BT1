# [H] CVE-2025-60938

## Summary
Severity: High
Advisory: CVE-2025-60938
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-60938
Type: osv

## Details
Emoncms 11.7.3 has a remote code execution vulnerability in the firmware upload feature that allows authenticated users to execute arbitrary commands on the target system. The vulnerability stems from insufficient input validation of user-controlled parameters including filename, port, baud_rate, core, and autoreset within the /admin/upload-custom-firmware endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60938.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60938
- https://github.com/emoncms/emoncms/issues/1941
