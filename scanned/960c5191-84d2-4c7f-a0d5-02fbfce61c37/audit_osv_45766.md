# [H] The HTTP/2 protocol allows a denial of service (server resource consumption) because request...

## Summary
Severity: High
Advisory: JLSEC-2026-3
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/JLSEC-2026-3
Type: osv

## Affected
- Julia: `Openresty_jll` — affected >=0 <1.27.1+0
- Julia: `libnode_jll` — affected >=18.12.1+0
- Julia: `nghttp2_jll` — affected >=0 <1.58.0+0

## Details
The HTTP/2 protocol allows a denial of service (server resource consumption) because request cancellation can reset many streams quickly, as exploited in the wild in August through October 2023.

## References
- http://www.openwall.com/lists/oss-security/2023/10/10/6
- http://www.openwall.com/lists/oss-security/2023/10/10/7
- http://www.openwall.com/lists/oss-security/2023/10/13/4
- http://www.openwall.com/lists/oss-security/2023/10/13/9
- http://www.openwall.com/lists/oss-security/2023/10/18/4
- http://www.openwall.com/lists/oss-security/2023/10/18/8
- http://www.openwall.com/lists/oss-security/2023/10/19/6
- http://www.openwall.com/lists/oss-security/2023/10/20/8
- http://www.openwall.com/lists/oss-security/2025/08/13/6
- https://access.redhat.com/security/cve/cve-2023-44487
- https://arstechnica.com/security/2023/10/how-ddosers-used-the-http-2-protocol-to-deliver-attacks-of-unprecedented-size/
- https://aws.amazon.com/security/security-bulletins/AWS-2023-011/
- https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/
- https://blog.cloudflare.com/zero-day-rapid-reset-http2-record-breaking-ddos-attack/
- https://blog.litespeedtech.com/2023/10/11/rapid-reset-http-2-vulnerablilty/
- https://blog.qualys.com/vulnerabilities-threat-research/2023/10/10/cve-2023-44487-http-2-rapid-reset-attack
- https://blog.vespa.ai/cve-2023-44487/
- https://bugzilla.proxmox.com/show_bug.cgi?id=4988
- https://bugzilla.redhat.com/show_bug.cgi?id=2242803
- https://bugzilla.suse.com/show_bug.cgi?id=1216123
