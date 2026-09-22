# [H] CVE-2019-11675

## Summary
Severity: High
Advisory: CVE-2019-11675
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-02
Source: https://osv.dev/vulnerability/CVE-2019-11675
Type: osv

## Details
The groonga-httpd package 6.1.5-1 for Debian sets the /var/log/groonga ownership to the groonga account, which might let local users obtain root access because of unsafe interaction with logrotate. For example, an attacker can exploit a race condition to insert a symlink from /var/log/groonga/httpd to /etc/bash_completion.d. NOTE: this is an issue in the Debian packaging of the Groonga HTTP server.

## References
- https://bugs.debian.org/928304
