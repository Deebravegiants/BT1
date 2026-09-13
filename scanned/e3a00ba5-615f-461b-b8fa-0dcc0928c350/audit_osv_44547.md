# [H] fast-uri vulnerable to authority injection via an unvalidated port in serialize

## Summary
Severity: High
Advisory: CVE-2026-84292
Aliases: GHSA-qw65-cvwx-89v3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84292
Type: osv

## Details
fast-uri serializes the port component of a URI without validating it. When recomposing the authority, the userinfo and host components are escaped but the port is concatenated verbatim, so a port value that is not a sequence of digits can inject authority delimiters, demoting the intended host to userinfo and pointing the authority at an attacker-controlled host. Both fast-uri and Node's URL read the result back as the attacker's host with no error, so re-validating the built URI does not catch it. This affects applications that build URIs from parts and assign untrusted data to the port component through the serialize, normalize, or equal functions in their object forms. The issue affects fast-uri versions before 2.4.6, from 3.0.0 before 3.1.7, and from 4.0.0 before 4.1.4. It is fixed in 2.4.6, 3.1.7, and 4.1.4, where recomposeAuthority rejects any port that is not a digit sequence per RFC 3986.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84292.json
- https://github.com/fastify/fast-uri/security/advisories/GHSA-qw65-cvwx-89v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-84292
