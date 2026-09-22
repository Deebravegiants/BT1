# [M] CVE-2026-12611

## Summary
Severity: Medium
Advisory: CVE-2026-12611
Aliases: GHSA-gpg9-4257-cfm3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-12611
Type: osv

## Details
A client may issue HTTP/2 requests to a Jetty server that result in blocking writes that are never unblocked, eventually causing all threads to be blocked and the whole server to become unresponsive.




This is caused by a race condition in the server when handling RST_STREAM frames and GOAWAY frames sent by the client.




The race condition "resets" the HTTP2Flusher.terminated, previously set to a non-null value, to the null value, allowing entries to be enqueued in the flusher that however will never be processed. These unprocessed entries are the ones that would unblock the write-blocked threads.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12611.json
- https://github.com/jetty/jetty.project/security/advisories/GHSA-gpg9-4257-cfm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-12611
