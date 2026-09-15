# [C] CVE-2023-27372

## Summary
Severity: Critical
Advisory: CVE-2023-27372
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-27372
Type: osv

## Details
SPIP before 4.2.1 allows Remote Code Execution via form values in the public area because serialization is mishandled. The fixed versions are 3.2.18, 4.0.10, 4.1.8, and 4.2.1.

## References
- https://packetstorm.news/files/id/171921
- https://packetstorm.news/files/id/173044
- http://packetstormsecurity.com/files/171921/SPIP-Remote-Command-Execution.html
- http://packetstormsecurity.com/files/173044/SPIP-4.2.1-Remote-Code-Execution.html
- https://blog.spip.net/Mise-a-jour-critique-de-securite-sortie-de-SPIP-4-2-1-SPIP-4-1-8-SPIP-4-0-10-et.html
- https://www.debian.org/security/2023/dsa-5367
- https://git.spip.net/spip/spip/commit/5aedf49b89415a4df3eb775eee3801a2b4b88266
- https://git.spip.net/spip/spip/commit/96fbeb38711c6706e62457f2b732a652a04a409d
