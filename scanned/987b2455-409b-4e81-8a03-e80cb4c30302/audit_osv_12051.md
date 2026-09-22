# [H] CVE-2018-1000857

## Summary
Severity: High
Advisory: CVE-2018-1000857
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000857
Type: osv

## Details
log-user-session version 0.7 and earlier contains a Directory Traversal vulnerability in Main SUID-binary /usr/local/bin/log-user-session that can result in User to root privilege escalation. This attack appear to be exploitable via Malicious unprivileged user executes the vulnerable binary/(remote) environment variable manipulation similar shell-shock also possible.

## References
- https://www.halfdog.net/Security/2018/LogUserSessionLocalRootPrivilegeEscalation/
