# [H] CVE-2017-1000112

## Summary
Severity: High
Advisory: CVE-2017-1000112
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000112
Type: osv

## Details
Linux kernel: Exploitable memory corruption due to UFO to non-UFO path switch. When building a UFO packet with MSG_MORE __ip_append_data() calls ip_ufo_append_data() to append. However in between two send() calls, the append path can be switched from UFO to non-UFO one, which leads to a memory corruption. In case UFO packet lengths exceeds MTU, copy = maxfraglen - skb->len becomes negative on the non-UFO path and the branch to allocate new skb is taken. This triggers fragmentation and computation of fraggap = skb_prev->len - maxfraglen. Fraggap can exceed MTU, causing copy = datalen - transhdrlen - fraggap to become negative. Subsequently skb_copy_and_csum_bits() writes out-of-bounds. A similar issue is present in IPv6 code. The bug was introduced in e89e9cf539a2 ("[IPv4/IPv6]: UFO Scatter-gather approach") on Oct 18 2005.

## References
- http://www.securitytracker.com/id/1039162
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2017:2931
- https://access.redhat.com/errata/RHSA-2019:1931
- https://access.redhat.com/errata/RHSA-2019:1932
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:3200
- https://access.redhat.com/errata/RHSA-2019:4159
- https://github.com/xairy/kernel-exploits/tree/master/CVE-2017-1000112
- https://www.exploit-db.com/exploits/45147/
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100262
- http://seclists.org/oss-sec/2017/q3/277
