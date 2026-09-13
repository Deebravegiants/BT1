# [H] CVE-2015-8630

## Summary
Severity: High
Advisory: CVE-2015-8630
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/CVE-2015-8630
Type: osv

## Details
The (1) kadm5_create_principal_3 and (2) kadm5_modify_principal functions in lib/kadm5/srv/svr_principal.c in kadmind in MIT Kerberos 5 (aka krb5) 1.12.x and 1.13.x before 1.13.4 and 1.14.x before 1.14.1 allow remote authenticated users to cause a denial of service (NULL pointer dereference and daemon crash) by specifying KADM5_POLICY with a NULL policy name.

## References
- http://rhn.redhat.com/errata/RHSA-2016-0532.html
- http://www.debian.org/security/2016/dsa-3466
- https://github.com/krb5/krb5/commit/b863de7fbf080b15e347a736fdda0a82d42f4f6b
- http://krbdev.mit.edu/rt/Ticket/Display.html?id=8342
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00059.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00110.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securitytracker.com/id/1034915
