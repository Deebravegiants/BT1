# [H] CVE-2010-2061

## Summary
Severity: High
Advisory: CVE-2010-2061
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2010-2061
Type: osv

## Details
rpcbind 0.2.0 does not properly validate (1) /tmp/portmap.xdr and (2) /tmp/rpcbind.xdr, which can be created by an attacker before the daemon is started.

## References
- https://access.redhat.com/security/cve/cve-2010-2061
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=583435#5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-2061
- https://security-tracker.debian.org/tracker/CVE-2010-2061
- https://www.openwall.com/lists/oss-security/2010/06/08/3
- https://www.openwall.com/lists/oss-security/2010/06/08/3
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-2061
