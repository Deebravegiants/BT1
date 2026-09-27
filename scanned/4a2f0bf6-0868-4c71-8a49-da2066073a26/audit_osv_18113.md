# [H] CVE-2020-24140

## Summary
Severity: High
Advisory: CVE-2020-24140
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2020-24140
Type: osv

## Details
Server-side request forgery in Wcms 0.3.2 let an attacker send crafted requests from the back-end server of a vulnerable web application via the pagename parameter to wex/html.php. It can help identify open ports, local network hosts and execute command on local services.

## References
- https://github.com/secwx/research/blob/main/cve/CVE-2020-24140.md
- https://github.com/vedees/wcms/issues/11
