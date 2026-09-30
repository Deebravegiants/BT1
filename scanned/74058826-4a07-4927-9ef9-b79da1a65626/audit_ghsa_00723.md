# [H] Regular Expression Denial of Service in websocket-extensions (RubyGem)

## Summary
Severity: High
Advisory: GHSA-g6wq-qcwm-j5g2
CVE: CVE-2020-7663
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-g6wq-qcwm-j5g2
Type: github-advisory

## Affected
- RubyGems: `websocket-extensions` — affected >=0 <0.1.5

## Details
### Impact

The ReDoS flaw allows an attacker to exhaust the server's capacity to process incoming requests by sending a WebSocket handshake request containing a header of the following form:

    Sec-WebSocket-Extensions: a; b="\c\c\c\c\c\c\c\c\c\c ...

That is, a header containing an unclosed string parameter value whose content is a repeating two-byte sequence of a backslash and some other character. The parser takes exponential time to reject this header as invalid, and this will block the processing of any other work on the same thread. Thus if you are running a single-threaded server, such a request can render your service completely unavailable.

### Patches

Users should upgrade to version 0.1.5.

### Workarounds

There are no known work-arounds other than disabling any public-facing WebSocket functionality you are operating.

### References

- https://blog.jcoglan.com/2020/06/02/redos-vulnerability-in-websocket-extensions/

## References
- https://github.com/faye/websocket-extensions-ruby/security/advisories/GHSA-g6wq-qcwm-j5g2
- https://nvd.nist.gov/vuln/detail/CVE-2020-7663
- https://github.com/faye/websocket-extensions-ruby/commit/aa156a439da681361ed6f53f1a8131892418838b
- https://blog.jcoglan.com/2020/06/02/redos-vulnerability-in-websocket-extensions
- https://github.com/faye/websocket-extensions-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/websocket-extensions/CVE-2020-7663.yml
- https://lists.debian.org/debian-lts-announce/2020/08/msg00031.html
- https://snyk.io/vuln/SNYK-RUBY-WEBSOCKETEXTENSIONS-570830
- https://usn.ubuntu.com/4502-1
