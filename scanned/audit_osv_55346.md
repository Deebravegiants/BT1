# [H] CVE-2025-33228

## Summary
Severity: High
Advisory: CVE-2025-33228
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-33228
Type: osv

## Details
NVIDIA Nsight Systems contains a vulnerability in the gfx_hotspot recipe, where an attacker could cause an OS command injection by supplying a malicious string to the process_nsys_rep_cli.py script if the script is invoked manually. A successful exploit of this vulnerability might lead to code execution, escalation of privileges, data tampering, denial of service, and information disclosure.

## References
- https://www.cve.org/CVERecord?id=CVE-2025-33228
- https://nvd.nist.gov/vuln/detail/CVE-2025-33228
- https://nvidia.custhelp.com/app/answers/detail/a_id/5755
