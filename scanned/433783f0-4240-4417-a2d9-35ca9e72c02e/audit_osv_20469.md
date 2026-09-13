# [C] CVE-2021-33990

## Summary
Severity: Critical
Advisory: CVE-2021-33990
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2021-33990
Type: osv

## Details
Liferay Portal 6.2.5 allows Command=FileUpload&Type=File&CurrentFolder=/ requests when frmfolders.html exists. NOTE: The vendor disputes this issue because the exploit reference link only shows frmfolders.html is accessible and does not demonstrate how an unauthorized user can upload a file.

## References
- http://packetstormsecurity.com/files/171701/Liferay-Portal-6.2.5-Insecure-Permissions.html
- https://github.com/fu2x2000/Liferay_exploit_Poc
