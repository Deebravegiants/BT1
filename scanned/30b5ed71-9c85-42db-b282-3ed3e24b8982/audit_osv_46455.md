# [H] CVE-2011-2189

## Summary
Severity: High
Advisory: CVE-2011-2189
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2011-10-10
Source: https://osv.dev/vulnerability/CVE-2011-2189
Type: osv

## Details
net/core/net_namespace.c in the Linux kernel 2.6.32 and earlier does not properly handle a high rate of creation and cleanup of network namespaces, which makes it easier for remote attackers to cause a denial of service (memory consumption) via requests to a daemon that requires a separate namespace per connection, as demonstrated by vsftpd.

## References
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629373
- http://patchwork.ozlabs.org/patch/88217/
- http://www.debian.org/security/2011/dsa-2305
- http://www.openwall.com/lists/oss-security/2011/06/06/10
- http://www.openwall.com/lists/oss-security/2011/06/06/20
- http://www.ubuntu.com/usn/USN-1288-1
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/720095
- https://bugzilla.redhat.com/show_bug.cgi?id=711134
- https://bugzilla.redhat.com/show_bug.cgi?id=711245
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629373
- http://patchwork.ozlabs.org/patch/88217/
- http://www.openwall.com/lists/oss-security/2011/06/06/10
- http://www.openwall.com/lists/oss-security/2011/06/06/20
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629373
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/720095
- https://bugzilla.redhat.com/show_bug.cgi?id=711134
- https://bugzilla.redhat.com/show_bug.cgi?id=711245
- http://patchwork.ozlabs.org/patch/88217/
- https://bugzilla.redhat.com/show_bug.cgi?id=711245
- https://bugzilla.redhat.com/show_bug.cgi?id=711134
