# [M] CVE-2023-31493

## Summary
Severity: Medium
Advisory: CVE-2023-31493
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2023-31493
Type: osv

## Details
RCE (Remote Code Execution) exists in ZoneMinder through 1.36.33 as an attacker can create a new .php log file in language folder, while executing a crafted payload and escalate privileges allowing execution of any commands on the remote system.

## References
- https://medium.com/@dk50u1/rce-remote-code-execution-in-zoneminder-up-to-1-36-33-0686f5bcd370
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31493.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31493
