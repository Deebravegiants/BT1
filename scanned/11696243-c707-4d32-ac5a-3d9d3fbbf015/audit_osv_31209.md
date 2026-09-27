# [C] BC Security Empire Path Traversal RCE

## Summary
Severity: Critical
Advisory: CVE-2024-6127
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-6127
Type: osv

## Details
BC Security Empire before 5.9.3 is vulnerable to a path traversal issue that can lead to remote code execution. A remote, unauthenticated attacker can exploit this vulnerability over HTTP by acting as a normal agent, completing all cryptographic handshakes, and then triggering an upload of payload data containing a malicious path.

## References
- https://github.com/BC-SECURITY/Empire/blob/8283bbc77250232eb493bf1f9104fdd0d468962a/CHANGELOG.md?plain=1#L102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6127.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6127
- https://vulncheck.com/advisories/empire-unauth-rce
- https://github.com/BC-SECURITY/Empire
- https://aceresponder.com/blog/exploiting-empire-c2-framework
- https://github.com/ACE-Responder/Empire-C2-RCE-PoC
