# [M] CVE-2026-12195

## Summary
Severity: Medium
Advisory: CVE-2026-12195
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-12195
Type: osv

## Details
myVesta is affected by an authenticated remote code execution vulnerability. Low privileged users can insert arbitrary commands as a part of the v_ftp_user parameter when deleting FTP usernames. This could result in the execution of commands as the admin user or takevoer of the admin user in myVesta.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12195.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12195
- https://github.com/myvesta/vesta/commit/95d7e43bf286d6881ca753dac93cb42d98cc7422
- https://projectblack.io/blog/local-ai-for-cyber-security/#myvesta-authenticated-rce
