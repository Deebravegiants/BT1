# [H] CVE-2019-7306

## Summary
Severity: High
Advisory: CVE-2019-7306
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2019-7306
Type: osv

## Details
Byobu Apport hook may disclose sensitive information since it automatically uploads the local user's .screenrc which may contain private hostnames, usernames and passwords. This issue affects: byobu

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-7306
- https://bugs.launchpad.net/ubuntu/+source/byobu/+bug/1827202
