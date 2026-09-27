# [C] Authenticated admin RCE in Invoice Ninja

## Summary
Severity: Critical
Advisory: CVE-2025-10009
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-10009
Type: osv

## Details
Incorrect handling of uploaded files in the admin "Restore" function in Invoice Ninja <= 5.11.72 allows attackers with admin credentials to execute arbitrary code on the server via uploaded .php files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10009.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10009
- https://github.com/invoiceninja/invoiceninja/commit/02151b570b226b4584a8e61b06b10be9366da3de
- https://github.com/invoiceninja/invoiceninja
