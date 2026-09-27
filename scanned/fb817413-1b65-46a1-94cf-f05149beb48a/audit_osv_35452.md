# [H] CVE-2025-8671

## Summary
Severity: High
Advisory: CVE-2025-8671
Aliases: GHSA-mrjm-qq9m-9mjq, RUSTSEC-2025-0070
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-8671
Type: osv

## Details
A mismatch caused by client-triggered server-sent stream resets between HTTP/2 specifications and the internal architectures of some HTTP/2 implementations may result in excessive server resource consumption leading to denial-of-service (DoS).  By opening streams and then rapidly triggering the server to reset them—using malformed frames or flow control errors—an attacker can exploit incorrect stream accounting. Streams reset by the server are considered closed at the protocol level, even though backend processing continues. This allows a client to cause the server to handle an unbounded number of concurrent streams on a single connection. This CVE will be updated as affected product details are released.

## References
- http://www.openwall.com/lists/oss-security/2025/08/13/6
- http://www.openwall.com/lists/oss-security/2025/09/18/1
- https://deepness-lab.org/publications/madeyoureset/
- https://galbarnahum.com/made-you-reset
- https://github.com/Kong/kong/discussions/14731
- https://kb.cert.org/vuls/id/767506
- https://support2.windriver.com/index.php?page=security-notices
- https://varnish-cache.org/security/VSV00017.html
- https://www.fastlystatus.com/incident/377810
- https://www.kb.cert.org/vuls/id/767506
- https://www.suse.com/support/kb/doc/?id=000021980
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8671.json
- https://github.com/h2o/h2o/security/advisories/GHSA-mrjm-qq9m-9mjq
- https://nvd.nist.gov/vuln/detail/CVE-2025-8671
- https://github.com/envoyproxy/envoy/issues/40739
- https://github.com/varnish/hitch/issues/397
- https://gitlab.isc.org/isc-projects/bind9/-/issues/5325
- https://github.com/h2o/h2o/commit/4729b661e3c6654198d2cc62997e1af58bef4b80
- https://www.imperva.com/blog/madeyoureset-turning-http-2-server-against-itself/
