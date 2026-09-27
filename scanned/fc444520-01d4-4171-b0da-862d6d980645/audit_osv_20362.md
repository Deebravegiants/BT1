# [C] CVE-2021-33226

## Summary
Severity: Critical
Advisory: CVE-2021-33226
Aliases: PYSEC-2023-47
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2021-33226
Type: osv

## Details
Buffer Overflow vulnerability in Saltstack v.3003 and before allows attacker to execute arbitrary code via the func variable in salt/salt/modules/status.py file. NOTE: this is disputed by third parties because an attacker cannot influence the eval input

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1208473
- https://github.com/saltstack/salt/blob/master/salt/modules/status.py
