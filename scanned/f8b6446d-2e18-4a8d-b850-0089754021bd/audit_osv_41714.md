# [H] Libevent: Off-by-one stack buffer overflow in dnsname_to_labels via crafted DNS server response

## Summary
Severity: High
Advisory: CVE-2026-63387
Aliases: GHSA-58rx-7448-jw47
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63387
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent has an off-by-one stack buffer overflow in evdns.c when dnsname_to_labels formats a name-bearing DNS record at the end of the 64 KB stack buffer allocated by evdns_server_request_format_response. The final-label check permits j plus label_len plus one to equal buf_len, after which the terminating null byte is written to buf[buf_len]. A crafted DNS server response containing PTR, CNAME, MX, NS, or SOA data can trigger the one-byte out-of-bounds write and crash or corrupt the process. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63387.json
- https://github.com/libevent/libevent/security/advisories/GHSA-58rx-7448-jw47
- https://nvd.nist.gov/vuln/detail/CVE-2026-63387
