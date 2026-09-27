# [C] Apache CXF: Unsafe deserialization of inbound JMS ObjectMessage

## Summary
Severity: Critical
Advisory: CVE-2026-66909
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-66909
Type: osv

## Details
Apache CXF's JMS transport deserializes the body of any inbound JMS ObjectMessage using native Java deserialization, with no type restrictions in place. Any attacker able to place a message on the service's JMS destination can submit a malicious serialized object, leading to denial of service or, if a suitable gadget class is on the classpath, remote code execution. The fix disables ObjectMessage deserialization by default, with a configuration switch to re-enable it if needed. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/18
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66909.json
- https://lists.apache.org/thread/lr5d4tg6tf7j29jmw8wt242oowonjqpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-66909
