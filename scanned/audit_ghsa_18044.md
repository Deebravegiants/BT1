# [H] Eclipse Jetty affected by MadeYouReset HTTP/2 vulnerability

## Summary
Severity: High
Advisory: GHSA-mmxm-8w33-wc4h
CVE: CVE-2025-5115
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-mmxm-8w33-wc4h
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=9.3.0 <9.4.58
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=10.0.0 <10.0.26
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=11.0.0 <11.0.26
- Maven: `org.eclipse.jetty.http2:jetty-http2-common` — affected >=12.0.0 <12.0.25
- Maven: `org.eclipse.jetty.http2:jetty-http2-common` — affected >=12.1.0.alpha0 <12.1.0.beta3

## Details
## Technical Details 
Below is a technical explanation of a newly discovered vulnerability in HTTP/2, which we refer to as “MadeYouReset.”

### MadeYouReset Vulnerability Summary
The MadeYouReset DDoS vulnerability is a logical vulnerability in the HTTP/2 protocol, that uses malformed HTTP/2 control frames in order to break the max concurrent streams limit - which results in resource exhaustion and distributed denial of service.

### Mechanism
The vulnerability uses malformed HTTP/2 control frames, or malformed flow, in order to make the server reset streams created by the client (using the RST_STREAM frame). 
The vulnerability could be triggered by several primitives, defined by the RFC of HTTP/2 (RFC 9113). The Primitives are:
1. WINDOW_UPDATE frame with an increment of 0 or an increment that makes the window exceed 2^31 - 1. (section 6.9 + 6.9.1)
2. HEADERS or DATA frames sent on a half-closed (remote) stream (which was closed using the END_STREAM flag). (note that for some implementations it's possible a CONTINUATION frame to trigger that as well - but it's very rare). (Section 5.1)
3. PRIORITY frame with a length other than 5. (section 6.3)
From our experience, the primitives are likely to exist in the decreasing order listed above.
Note that based on the implementation of the library, other primitives (which are not defined by the RFC) might exist - meaning scenarios in which RST_STREAM is not supposed to be sent, but in the implementation it does. On the other hand - some RFC-defined primitives might not work, even though they are defined by the RFC (as some implementations are not fully complying with RFC). For example, some implementations we’ve seen discard the PRIORITY frame - and thus does not return RST_STREAM, and some implementations send GO_AWAY when receiving a WINDOW_UPDATE frame with increment of 0.

The vulnerability takes advantage of a design flaw in the HTTP/2 protocol - While HTTP/2 has a limit on the number of concurrently active streams per connection (which is usually 100, and is set by the parameter SETTINGS_MAX_CONCURRENT_STREAMS), the number of active streams is not counted correctly - when a stream is reset, it is immediately considered not active, and thus unaccounted for in the active streams counter. 
While the protocol does not count those streams as active, the server’s backend logic still processes and handles the requests that were canceled.

Thus, the attacker can exploit this vulnerability to cause the server to handle an unbounded number of concurrent streams from a client on the same connection. The exploitation is very simple: the client issues a request in a stream, and then sends the control frame that causes the server to send a RST_STREAM.

### Attack Flow
For example, a possible attack scenario can be: 
1. Attacker opens an HTTP/2 connection to the server.
2. Attacker sends HEADERS frame with END_STREAM flag on a new stream X.  
3. Attacker sends WINDOW_UPDATE for stream X with flow-control window of 0.
4. The server receives the WINDOW_UPDATE and immediately sends RST_STREAM for stream X to the client (+ decreases the active streams counter by 1).

The attacker can repeat steps 2+3 as rapidly as it is capable, since the active streams counter never exceeds 1 and the attacker does not need to wait for the response from the server.
This leads to resource exhaustion and distributed denial of service vulnerabilities with an impact of: CPU overload and/or memory exhaustion (implementation dependant)

### Comparison to Rapid Reset
The vulnerability takes advantage of a design flow in the HTTP/2 protocol that was also used in the Rapid Reset vulnerability (CVE-2023-44487) which was exploited as a zero-day in the wild in August 2023 to October 2023, against multiple services and vendors.
The Rapid Reset vulnerability uses RST_STREAM frames sent from the client, in order to create an unbounded amount of concurrent streams - it was given a CVSS score of 7.5.
Rapid Reset was mostly mitigated by limiting the number/rate of RST_STREAM sent from the client, which does not mitigate the MadeYouReset attack - since it triggers the server to send a RST_STREAM.

### Suggested Mitigations for MadeYouReset
A quick and easy mitigation will be to limit the number/rate of RST_STREAMs sent from the server.
It is also possible to limit the number/rate of control frames sent by the client (e.g. WINDOW_UPDATE and PRIORITY), and treat protocol flow errors as a connection error.

As mentioned in our previous message, this is a protocol-level vulnerability that affects multiple vendors and implementations. Given its broad impact, it is the shared responsibility of all parties involved to handle the disclosure process carefully and coordinate mitigations effectively.


If you have any questions, we will be happy to clarify or schedule a Zoom call.

Gal, Anat and Yaniv.



## Jetty's Team Notes

### Impact
A denial of service vulnerability similar to [Rapid Reset](https://github.com/jetty/jetty.project/security/advisories/GHSA-c745-7wm4-7738), but where the client triggers a reset from the server by sending a malformed or invalid frame.
In particular, this may be triggered by WINDOW_UPDATE frames that are invalid (e.g. with `delta==0` or when the delta makes the window exceed `2^31-1`).

### Patches
Patch has been merged into 12.0.x mainline via https://github.com/jetty/jetty.project/pull/13449.

### Workarounds
No workarounds apart disabling HTTP/2.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-mmxm-8w33-wc4h
- https://nvd.nist.gov/vuln/detail/CVE-2025-5115
- https://github.com/jetty/jetty.project/pull/13449
- https://github.com/jetty/jetty.project/commit/f9ee3904788b08203ed62c95a560d951da37bdb1
- https://github.com/jetty/jetty.project
- https://github.com/jetty/jetty.project/releases/tag/jetty-10.0.26
- https://github.com/jetty/jetty.project/releases/tag/jetty-11.0.26
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.0.25
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.1.0
- https://github.com/jetty/jetty.project/releases/tag/jetty-9.4.58.v20250814
- https://lists.debian.org/debian-lts-announce/2025/09/msg00014.html
- https://www.kb.cert.org/vuls/id/767506
- http://www.openwall.com/lists/oss-security/2025/08/20/4
- http://www.openwall.com/lists/oss-security/2025/09/17/1
