# [C] CVE-2017-14135

## Summary
Severity: Critical
Advisory: CVE-2017-14135
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14135
Type: osv

## Details
enigma2-plugins/blob/master/webadmin/src/WebChilds/Script.py in the webadmin plugin for opendreambox 2.0.0 allows remote attackers to execute arbitrary OS commands via shell metacharacters in the command parameter to the /script URI.

## References
- https://the-infosec.com/2017/07/05/from-shodan-to-rce-opendreambox-2-0-0-code-execution/
