# [C] Apache CXF: JwtRequestCodeFilter silently overrides outer PKCE and nonce parameters

## Summary
Severity: Critical
Advisory: CVE-2026-63687
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-63687
Type: osv

## Details
Apache CXF's JwtRequestCodeFilter copies all claims from a signed request JWT into the authorization parameter map without excluding security-sensitive parameters. A client that can produce a validly-signed request JWT (e.g., one whose client_secret is known or compromised) can thereby substitute the code_challenge, code_challenge_method, nonce, and state values that were set in the outer HTTP request, undermining PKCE integrity and OpenID Connect replay protection. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/22
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63687.json
- https://lists.apache.org/thread/drcq4chmt0btx86f17o47j17r378hzpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-63687
