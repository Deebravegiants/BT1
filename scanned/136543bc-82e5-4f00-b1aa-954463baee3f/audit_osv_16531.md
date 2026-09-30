# [H] CVE-2019-7652

## Summary
Severity: High
Advisory: CVE-2019-7652
CVSS: 7.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-7652
Type: osv

## Details
TheHive Project UnshortenLink analyzer before 1.1, included in Cortex-Analyzers before 1.15.2, has SSRF. To exploit the vulnerability, an attacker must create a new analysis, select URL for Data Type, and provide an SSRF payload like "http://127.0.0.1:22" in the Data parameter. The result can be seen in the main dashboard. Thus, it is possible to do port scans on localhost and intranet hosts.

## References
- http://packetstormsecurity.com/files/152804/TheHive-Project-Cortex-2.1.3-Server-Side-Request-Forgery.html
- https://blog.thehive-project.org/2019/02/11/unshortenlink-ssrf-and-cortex-analyzers-1-15-2/
