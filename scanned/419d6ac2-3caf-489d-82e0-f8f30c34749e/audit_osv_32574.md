# [C] CVE-2025-32453

## Summary
Severity: Critical
Advisory: CVE-2025-32453
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2025-32453
Type: osv

## Details
Incorrect default permissions for some Intel(R) Graphics Driver software within Ring 2: Privileged Process may allow an escalation of privilege. Unprivileged software adversary with an authenticated user combined with a high complexity attack may enable escalation of privilege. This result may potentially occur via local access when attack requirements are present without special internal knowledge and requires active user interaction. The potential vulnerability may impact the confidentiality (high), integrity (high) and availability (high) of the vulnerable system, resulting in subsequent system confidentiality (none), integrity (none) and availability (none) impacts.

## References
- https://intel.com/content/www/us/en/security-center/advisory/intel-sa-01385.html
