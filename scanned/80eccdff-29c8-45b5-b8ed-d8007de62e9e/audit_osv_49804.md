# [H] CVE-2019-19191

## Summary
Severity: High
Advisory: CVE-2019-19191
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-19191
Type: osv

## Details
Shibboleth Service Provider (SP) 3.x before 3.1.0 shipped a spec file that calls chown on files in a directory controlled by the service user (the shibd account) after installation. This allows the user to escalate to root by pointing symlinks to files such as /etc/shadow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00017.html
- https://bugzilla.suse.com/show_bug.cgi?id=1157471
- https://issues.shibboleth.net/jira/browse/SSPCPP-874
