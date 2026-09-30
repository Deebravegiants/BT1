# [H] CVE-2023-46047

## Summary
Severity: High
Advisory: CVE-2023-46047
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-46047
Type: osv

## Details
An issue in Sane 1.2.1 allows a local attacker to execute arbitrary code via a crafted file to the sanei_configure_attach() function. NOTE: this is disputed because there is no expectation that the product should be starting with an attacker-controlled configuration file.

## References
- http://packetstormsecurity.com/files/176818/sane-1.2.1-Null-Pointer.html
- http://seclists.org/fulldisclosure/2024/Jan/64
- https://gitlab.com/sane-project/backends/-/issues/708
