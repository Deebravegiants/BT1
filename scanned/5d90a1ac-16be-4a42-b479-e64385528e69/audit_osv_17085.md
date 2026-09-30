# [C] CVE-2020-12079

## Summary
Severity: Critical
Advisory: CVE-2020-12079
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/CVE-2020-12079
Type: osv

## Details
Beaker before 0.8.9 allows a sandbox escape, enabling system access and code execution. This occurs because Electron context isolation is not used, and therefore an attacker can conduct a prototype-pollution attack against the Electron internal messaging API.

## References
- https://github.com/beakerbrowser/beaker/issues/1519
- https://github.com/beakerbrowser/beaker/releases/tag/0.8.9
