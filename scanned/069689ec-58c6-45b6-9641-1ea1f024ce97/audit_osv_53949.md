# [H] CVE-2023-33865

## Summary
Severity: High
Advisory: CVE-2023-33865
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-33865
Type: osv

## Details
RenderDoc before 1.27 allows local privilege escalation via a symlink attack. It relies on the /tmp/RenderDoc directory regardless of ownership.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00008.html
- https://renderdoc.org/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00023.html
- https://security.gentoo.org/glsa/202311-10
- http://packetstormsecurity.com/files/172804/RenderDoc-1.26-Local-Privilege-Escalation-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2023/Jun/2
- https://www.qualys.com/2023/06/06/renderdoc/renderdoc.txt
