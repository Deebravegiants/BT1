# [H] CVE-2023-46052

## Summary
Severity: High
Advisory: CVE-2023-46052
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-46052
Type: osv

## Details
Sane 1.2.1 heap bounds overwrite in init_options() from backend/test.c via a long init_mode string in a configuration file. NOTE: this is disputed because there is no expectation that test.c code should be executed with an attacker-controlled configuration file.

## References
- http://packetstormsecurity.com/files/176823/sane-1.2.1-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2024/Jan/69
- https://gitlab.com/sane-project/backends/-/issues/709
