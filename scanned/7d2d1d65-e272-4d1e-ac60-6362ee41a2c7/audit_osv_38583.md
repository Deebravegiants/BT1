# [H] CVE-2026-40691

## Summary
Severity: High
Advisory: CVE-2026-40691
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-40691
Type: osv

## Details
In Unbound 1.9.0 up to and including 1.25.1, when a DNSCrypt query is received over TCP, the routine that encrypts the reply in place fails to bound the reply length against the destination buffer size. The size clamp that protects the UDP path is not applied on the TCP path, so a reply larger than 65504 bytes is shifted forward by 48 bytes inside a buffer of capacity equal to 'msg-buffer-size', writing past the end of the heap allocation. A single malicious encrypted query crashes the resolver and lead to denial of service. This vulnerability needs Unbound to be compiled with DNSCrypt support ('--enable-dnscrypt') and the 'dnscrypt:' clause to be configured and enabled for the listening interfaces.

## References
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-40691.txt
