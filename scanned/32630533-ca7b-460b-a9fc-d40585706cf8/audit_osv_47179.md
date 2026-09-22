# [M] CVE-2016-10100

## Summary
Severity: Medium
Advisory: CVE-2016-10100
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-01-02
Source: https://osv.dev/vulnerability/CVE-2016-10100
Type: osv

## Details
Borg (aka BorgBackup) before 1.0.9 has a flaw in the way duplicate archive names were processed during manifest recovery, potentially allowing an attacker to overwrite an archive.

## References
- http://www.securityfocus.com/bid/95203
- http://borgbackup.readthedocs.io/en/stable/changes.html#pre-1-0-9-manifest-spoofing-vulnerability
