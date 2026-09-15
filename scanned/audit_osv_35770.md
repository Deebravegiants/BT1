# [H] CVE-2026-14336

## Summary
Severity: High
Advisory: CVE-2026-14336
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-14336
Type: osv

## Details
PIA's OIDC issuer allowlist for Jenkins tokens uses a bare string-prefix check (issuer.startswith(' https://ci.eclipse.org ') in is_issuer_known, pia/models.py:139) instead of validating the issuer as a properly host-bounded URL. An attacker can craft an issuer such as  https://ci.eclipse.org@evil.host  (userinfo trick) or  https://ci.eclipse.org.evil.host  (suffix trick) that satisfies the prefix check while pointing the OIDC discovery and JWKS fetches at a server the attacker controls. An unauthenticated caller of POST /v1/upload/sbom can use this to force PIA to make outbound HTTP(S) requests to an arbitrary attacker-chosen host, and to have oidc.verify_token accept a JWT signed with the attacker's own key.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/154
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14336.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14336
- https://github.com/eclipse-csi/pia
