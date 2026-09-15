# [H] Privilege escalation in mk_informix plugin

## Summary
Severity: High
Advisory: CVE-2024-28824
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-22
Source: https://osv.dev/vulnerability/CVE-2024-28824
Type: osv

## Details
Least privilege violation and reliance on untrusted inputs in the mk_informix Checkmk agent plugin before Checkmk 2.3.0b4 (beta), 2.2.0p24, 2.1.0p41 and 2.0.0 (EOL) allows local users to escalate privileges.

## References
- https://checkmk.com/werk/16198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28824.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28824
