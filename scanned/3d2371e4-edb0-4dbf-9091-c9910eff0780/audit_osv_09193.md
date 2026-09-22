# [H] CVE-2016-8867

## Summary
Severity: High
Advisory: CVE-2016-8867
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8867
Type: osv

## Details
Docker Engine 1.12.2 enabled ambient capabilities with misconfigured capability policies. This allowed malicious images to bypass user permissions to access files within the container filesystem or mounted volumes.

## References
- http://www.securitytracker.com/id/1037203
- http://www.securityfocus.com/bid/94228
- https://www.docker.com/docker-cve-database
