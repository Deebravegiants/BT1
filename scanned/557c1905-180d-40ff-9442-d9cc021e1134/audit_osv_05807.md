# [C] HAProxy - Integer Overflow in FCGI Demux Record Length Field

## Summary
Severity: Critical
Advisory: BIT-haproxy-2026-55203
Aliases: CVE-2026-55203
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-haproxy-2026-55203
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=0 <3.4.1

## Details
HAProxy through 3.4.0, fixed in commit 5985276, contains an integer overflow vulnerability in the fcgi_conn structure's drl field that allows buffer misparse as new FCGI record headers. When contentLength is 65535 and paddingLength is 1 or more, the drl field wraps to 0, causing incorrect record consumption and allowing malicious FastCGI backends to desynchronize the FCGI framing parser, potentially causing request routing errors, response smuggling, or memory safety issues.

## References
- https://github.com/haproxy/haproxy/commit/5985276735777634d8c85f1d73bb7764aab0d6dd
- https://nvd.nist.gov/vuln/detail/CVE-2026-55203
- https://www.vulncheck.com/advisories/haproxy-integer-overflow-in-fcgi-demux-record-length-field
