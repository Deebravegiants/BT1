# [C] CVE-2026-42168

## Summary
Severity: Critical
Advisory: CVE-2026-42168
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-42168
Type: osv

## Details
django-pyas2 through 1.2.3 is vulnerable to OS command injection via the cmd_receive and cmd_send fields on the Partner model. These fields are passed directly to os.system() in pyas2/utils.py without sanitization, allowing an authenticated admin user to execute arbitrary commands on the server when an AS2 message is received or sent.

## References
- https://github.com/abhishek-ram/django-pyas2/releases/tag/v1.2.3
- https://github.com/m4ty-m/vulnerability-research/tree/main/CVE-2026-42168
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42168.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42168
- https://github.com/abhishek-ram/django-pyas2
