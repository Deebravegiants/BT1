# [H] Libexpat: expat: improper restriction of xml entity expansion depth in libexpat

## Summary
Severity: High
Advisory: CVE-2024-8176
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-14
Source: https://osv.dev/vulnerability/CVE-2024-8176
Type: osv

## Details
A stack overflow vulnerability exists in the libexpat library due to the way it handles recursive entity expansion in XML documents. When parsing an XML document with deeply nested entity references, libexpat can be forced to recurse indefinitely, exhausting the stack space and causing a crash. This issue could lead to denial of service (DoS) or, in some cases, exploitable memory corruption, depending on the environment and library usage.

## References
- http://seclists.org/fulldisclosure/2025/May/10
- http://seclists.org/fulldisclosure/2025/May/11
- http://seclists.org/fulldisclosure/2025/May/12
- http://seclists.org/fulldisclosure/2025/May/6
- http://seclists.org/fulldisclosure/2025/May/7
- http://seclists.org/fulldisclosure/2025/May/8
- http://www.openwall.com/lists/oss-security/2025/03/15/1
- http://www.openwall.com/lists/oss-security/2025/09/24/11
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/libexpat/libexpat/
- https://github.com/libexpat/libexpat/blob/R_2_7_0/expat/Changes#L40-L52
- https://security-tracker.debian.org/tracker/CVE-2024-8176
- https://ubuntu.com/security/CVE-2024-8176
- https://www.kb.cert.org/vuls/id/760160
- https://access.redhat.com/errata/RHSA-2025:13681
- https://access.redhat.com/errata/RHSA-2025:22033
- https://access.redhat.com/errata/RHSA-2025:22034
- https://access.redhat.com/errata/RHSA-2025:22035
- https://access.redhat.com/errata/RHSA-2025:22607
