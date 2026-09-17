# [H] CVE-2020-28884

## Summary
Severity: High
Advisory: CVE-2020-28884
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-28
Source: https://osv.dev/vulnerability/CVE-2020-28884
Type: osv

## Details
Liferay Portal Server tested on 7.3.5 GA6, 7.2.0 GA1 is affected by OS Command Injection. An administrator user can inject Groovy script to execute any OS command on the Liferay Portal Sever. NOTE: The developer disputes this as a vulnerability since it is a feature for administrators to run groovy scripts and therefore not a design flaw.

## References
- https://medium.com/%40tranpdanh/some-way-to-execute-os-command-in-liferay-portal-84498bde18d3
- https://learn.liferay.com/dxp/latest/en/system-administration/using-the-script-engine/running-scripts-from-the-script-console.html
