# [H] CVE-2020-15133

## Summary
Severity: High
Advisory: CVE-2020-15133
Aliases: GHSA-2v5c-755p-p4gv
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2020-07-31
Source: https://osv.dev/vulnerability/CVE-2020-15133
Type: osv

## Details
In faye-websocket before version 0.11.0, there is a lack of certification validation in TLS handshakes. The `Faye::WebSocket::Client` class uses the `EM::Connection#start_tls` method in EventMachine to implement the TLS handshake whenever a `wss:` URL is used for the connection. This method does not implement certificate verification by default, meaning that it does not check that the server presents a valid and trusted TLS certificate for the expected hostname. That means that any `wss:` connection made using this library is vulnerable to a man-in-the-middle attack, since it does not confirm the identity of the server it is connected to. For further background information on this issue, please see the referenced GitHub Advisory. Upgrading `faye-websocket` to v0.11.0 is recommended.

## References
- https://blog.jcoglan.com/2020/07/31/missing-tls-verification-in-faye/
- https://github.com/faye/faye-websocket-ruby/security/advisories/GHSA-2v5c-755p-p4gv
