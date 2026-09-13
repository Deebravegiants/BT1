# [C] Flowintel Arbitrary Log File Path Allows Remote Code Execution via Template Injection

## Summary
Severity: Critical
Advisory: CVE-2026-81743
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81743
Type: osv

## Details
Affected versions of Flowintel allow the LOG_FILE configuration value to be modified through system settings without restricting it to a filename inside the intended log directory.


Because the application constructs the log destination from this configurable value, an administrator could set LOG_FILE to an arbitrary filesystem path. Since attackers can influence logged content, this enables controlled data to be written into unintended files. The upstream commit specifically describes an exploitation chain in which an attacker injects a template into a chosen file and subsequently abuses application rendering behavior to execute code.

The patch removes LOG_FILE from the web-editable settings, introduces validate_log_file_name() to reject absolute paths, traversal, Windows paths, null bytes, and directory components, and centralizes log path construction through resolve_log_file_path().

Version impacted: >=3.3.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81743
- https://github.com/flowintel/flowintel/commit/13785ee5d70a54d0ac97ba89dd31a478a86fc161
- https://github.com/flowintel/flowintel
