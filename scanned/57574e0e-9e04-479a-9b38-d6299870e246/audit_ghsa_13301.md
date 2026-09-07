# [H] SwiftTerm Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-jq43-q8mx-r7mq
CVE: CVE-2022-23465
CWE: CWE-94
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-jq43-q8mx-r7mq
Type: github-advisory

## Affected
- SwiftURL: `github.com/migueldeicaza/SwiftTerm` — affected >=0 <1.2.0

## Details
### Impact

Attacker could modify the window title via a certain character escape sequence and then insert it back to the command line in the user's terminal, e.g. when the user views a file containing the malicious sequence, which could allow the attacker to execute arbitrary commands.

### Credit
These bugs were found and disclosed by David Leadbeater <dgl@dgl.cx> (@dgl at Github.com)

### Patches

Fixed in version ce596e0dc8cdb288bc7ed5c6a59011ee3a8dc171

### Workarounds

There are no workarounds available

### References

Similar exploits to this existed in the past, for terminal emulators:

https://nvd.nist.gov/vuln/detail/CVE-2003-0063
https://nvd.nist.gov/vuln/detail/CVE-2008-2383

Additional background and information is also available:

https://marc.info/?l=bugtraq&m=104612710031920&w=2
https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=510030

## References
- https://github.com/migueldeicaza/SwiftTerm/security/advisories/GHSA-jq43-q8mx-r7mq
- https://nvd.nist.gov/vuln/detail/CVE-2022-23465
- https://github.com/migueldeicaza/SwiftTerm/commit/a94e6b24d24ce9680ad79884992e1dff8e150a31
- https://github.com/migueldeicaza/SwiftTerm
