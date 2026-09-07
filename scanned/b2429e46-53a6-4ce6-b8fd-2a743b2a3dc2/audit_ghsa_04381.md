# [M] SwiftNIO: CRLF Injection in outbound HTTP request URI via NIOHTTPRequestHeadersValidator

## Summary
Severity: Medium
Advisory: GHSA-cq87-8r7h-962v
CVE: CVE-2026-28970
CWE: CWE-93
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N/E:U (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-cq87-8r7h-962v
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio` — affected >=2.0.0 <2.100.0

## Details
Programs using swift-nio is vulnerable to HTTP request smuggling and HTTP response splitting attacks, caused by insufficient validation of outbound HTTP/1.1 request and response start line components.

This vulnerability affects all swift-nio versions from 2.0.0 to 2.99.0. It is fixed in 2.100.0 and later releases.                                                                                         
                  
This vulnerability is caused by the `NIOHTTPRequestHeadersValidator` and `NIOHTTPResponseHeadersValidator` channel handlers only validating header field names and values, while leaving the request URI, request method, and response reason phrase unvalidated. An attacker who can influence the content of these fields — for example by controlling a URL path or a custom HTTP method in a proxy application — can inject CR/LF sequences or other control characters into the HTTP start line. This allows construction of arbitrary additional HTTP requests or responses on the wire, a classic HTTP request smuggling or HTTP response splitting attack.

Exploiting this vulnerability requires the attacker to influence the content of outbound HTTP start line fields. In proxy applications that forward attacker-controlled URIs or methods, this is straightforward. For clients, a malicious server that triggers a redirect to a crafted URL could exploit the URI validation gap. For servers, any client that can cause the server to emit a crafted response reason phrase could exploit the response splitting gap.                                                                                                                                          
                  
In vulnerable applications, where attacker controlled data is supplied to these fields, the attack is low-effort: injecting a CRLF sequence into a URI or reason phrase requires only a single crafted request. Successful exploitation can allow an attacker to smuggle additional HTTP requests past intermediaries or split HTTP responses, potentially bypassing WAFs or poisoning web caches. However, most applications are not vulnerable at all.
                                                                                                                                                                                                            
The risk can be mitigated by ensuring that all user-controlled input is sanitized before being used in HTTP start line components. However, this mitigation places the burden on application developers and is error-prone.
                                                                                                                                                                                                            
The issue is fixed by extending `NIOHTTPRequestHeadersValidator` to validate request URIs against the character set defined in RFC 9112 Section 3.2 and RFC 3986 Section 3, and to validate custom HTTP methods against the token grammar defined in RFC 9110. `NIOHTTPResponseHeadersValidator` is extended to validate custom response reason phrases against RFC 9112 Section 4. Applications that use these validator channel handlers — which are installed by default when using `addHTTPClientHandlers()` or `addHTTPServerHandlers()` — will reject invalid outbound messages with an HTTPParserError.invalidHeaderToken error rather than emitting them to the network.

SwiftNIO is grateful to @kuranikaran and @YLChen-007 for their reporting and assistance with the project's process.

## References
- https://github.com/apple/swift-nio/security/advisories/GHSA-cq87-8r7h-962v
- https://github.com/apple/swift-nio
