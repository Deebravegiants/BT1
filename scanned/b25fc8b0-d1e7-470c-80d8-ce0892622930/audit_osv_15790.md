# [H] CVE-2019-19684

## Summary
Severity: High
Advisory: CVE-2019-19684
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19684
Type: osv

## Details
nopCommerce v4.2.0 allows privilege escalation via file upload in Presentation/Nop.Web/Admin/Areas/Controllers/PluginController.cs via Admin/FacebookAuthentication/Configure because it is possible to upload a crafted Facebook Auth plugin.

## References
- https://github.com/klezVirus/cves/tree/master/NopCommerce/Privilege%20Escalation%20via%20Plugin%20Upload
