# [M] CVE-2016-10099

## Summary
Severity: Medium
Advisory: CVE-2016-10099
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-01-02
Source: https://osv.dev/vulnerability/CVE-2016-10099
Type: osv

## Details
Borg (aka BorgBackup) before 1.0.9 has a flaw in the cryptographic protocol used to authenticate the manifest (list of archives), potentially allowing an attacker to spoof the list of archives.

## References
- http://borgbackup.readthedocs.io/en/stable/changes.html#pre-1-0-9-manifest-spoofing-vulnerability
- http://www.securityfocus.com/bid/95205
