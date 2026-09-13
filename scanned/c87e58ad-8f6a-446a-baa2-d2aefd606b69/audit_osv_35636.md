# [C] Local privilege escalation in ANSSI’s DFIR-ORC

## Summary
Severity: Critical
Advisory: CVE-2026-11958
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-11958
Type: osv

## Details
Local privilege escalation by loading DLLs from a shared temporary directory in ANSSI’s DFIR-ORC, versions 10.2.7 and prior. An attacker with prior access to the system, can place a malicious DLL in C:\Windows\Temp and wait for the application to be executed. Because DFIR-ORC is extracted and executed from that location with administrative privileges, the malicious library can be loaded automatically, allowing the attacker to gain administrator privileges on the affected machine.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11958.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11958
- https://github.com/DFIR-ORC/dfir-orc/releases/tag/v10.3.0
- https://www.incibe.es/en/incibe-cert/notices/aviso/local-privilege-escalation-anssis-dfir-orc
