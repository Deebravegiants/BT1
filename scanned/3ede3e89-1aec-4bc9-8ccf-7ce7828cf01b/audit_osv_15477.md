# [H] CVE-2019-16701

## Summary
Severity: High
Advisory: CVE-2019-16701
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-25
Source: https://osv.dev/vulnerability/CVE-2019-16701
Type: osv

## Details
pfSense through 2.3.4 through 2.4.4-p3 allows Remote Code Injection via a methodCall XML document with a pfsense.exec_php call containing shell metacharacters in a parameter value.

## References
- https://github.com/pfsense/pfsense/commits/master
- http://packetstormsecurity.com/files/154587/pfSense-2.3.4-2.4.4-p3-Remote-Code-Injection.html
- https://hackernews.blog/pfsense-2-3-4-2-4-4-p3-remote-code-injection/#more
