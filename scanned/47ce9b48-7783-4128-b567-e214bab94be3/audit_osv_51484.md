# [C] CVE-2021-30633

## Summary
Severity: Critical
Advisory: CVE-2021-30633
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-10-08
Source: https://osv.dev/vulnerability/CVE-2021-30633
Type: osv

## Details
Use after free in Indexed DB API in Google Chrome prior to 93.0.4577.82 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-30633
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PM7MOYYHJSWLIFZ4TPJTD7MSA3HSSLV2/
- https://chromereleases.googleblog.com/2021/09/stable-channel-update-for-desktop.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4DDW7HAHTS3SDVXBQUY4SURELO5D4X7R/
- https://crbug.com/1247766
