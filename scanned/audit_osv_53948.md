# [C] CVE-2023-33864

## Summary
Severity: Critical
Advisory: CVE-2023-33864
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-33864
Type: osv

## Details
StreamReader::ReadFromExternal in RenderDoc before 1.27 allows an Integer Overflow with a resultant Buffer Overflow. It uses uint32_t(m_BufferSize-m_InputSize) even though m_InputSize can exceed m_BufferSize.

## References
- https://renderdoc.org/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/07/msg00023.html
- https://security.gentoo.org/glsa/202311-10
- http://packetstormsecurity.com/files/172804/RenderDoc-1.26-Local-Privilege-Escalation-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2023/Jun/2
- https://www.qualys.com/2023/06/06/renderdoc/renderdoc.txt
