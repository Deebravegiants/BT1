# [C] CVE-2018-12562

## Summary
Severity: Critical
Advisory: CVE-2018-12562
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12562
Type: osv

## Details
An issue was discovered in the cantata-mounter D-Bus service in Cantata through 2.3.1. The wrapper script 'mount.cifs.wrapper' uses the shell to forward the arguments to the actual mount.cifs binary. The shell evaluates wildcards (such as in an injected string:/home/../tmp/* string).

## References
- https://github.com/CDrummond/cantata/commit/afc4f8315d3e96574925fb530a7004cc9e6ce3d3
- http://www.openwall.com/lists/oss-security/2018/06/18/1
