# [C] CVE-2011-1935

## Summary
Severity: Critical
Advisory: CVE-2011-1935
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-20
Source: https://osv.dev/vulnerability/CVE-2011-1935
Type: osv

## Details
pcap-linux.c in libpcap 1.1.1 before commit ea9432fabdf4b33cbc76d9437200e028f1c47c93 when snaplen is set may truncate packets, which might allow remote attackers to send arbitrary data while avoiding detection via crafted packets.

## References
- http://article.gmane.org/gmane.network.tcpdump.devel/4968
- http://thread.gmane.org/gmane.network.tcpdump.devel/5018
- http://www.openwall.com/lists/oss-security/2011/05/19/11
- http://www.openwall.com/lists/oss-security/2014/02/08/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623868
- https://security-tracker.debian.org/tracker/CVE-2011-1935/
- http://www.openwall.com/lists/oss-security/2011/05/19/11
- http://www.openwall.com/lists/oss-security/2014/02/08/5
- http://thread.gmane.org/gmane.network.tcpdump.devel/5018
- http://www.openwall.com/lists/oss-security/2011/05/19/11
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623868
- http://article.gmane.org/gmane.network.tcpdump.devel/4968
- http://thread.gmane.org/gmane.network.tcpdump.devel/5018
- http://www.openwall.com/lists/oss-security/2011/05/19/11
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=623868
- https://security-tracker.debian.org/tracker/CVE-2011-1935/
- http://article.gmane.org/gmane.network.tcpdump.devel/4968
- http://thread.gmane.org/gmane.network.tcpdump.devel/5018
- http://www.openwall.com/lists/oss-security/2011/05/19/11
- https://bugs.debian.org/cgi-bin/bugreport.cgi?att=1%3Bbug=623868%3Bfilename=0001-Fix-the-calculation-of-the-frame-size-in-memory-mapp.patch%3Bmsg=10
