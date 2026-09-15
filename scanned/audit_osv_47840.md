# [C] CVE-2017-13715

## Summary
Severity: Critical
Advisory: CVE-2017-13715
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13715
Type: osv

## Details
The __skb_flow_dissect function in net/core/flow_dissector.c in the Linux kernel before 4.3 does not ensure that n_proto, ip_proto, and thoff are initialized, which allows remote attackers to cause a denial of service (system crash) or possibly execute arbitrary code via a single crafted MPLS packet.

## References
- http://seclists.org/oss-sec/2017/q3/345
- http://www.securityfocus.com/bid/100517
- https://github.com/torvalds/linux/commit/a6e544b0a88b53114bfa5a57e21b7be7a8dfc9d0
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a6e544b0a88b53114bfa5a57e21b7be7a8dfc9d0
