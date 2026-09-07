# [H] Redlib allows a Denial of Service via DEFLATE Decompression Bomb in restore_preferences Form

## Summary
Severity: High
Advisory: GHSA-g8vq-v3mg-7mrg
CVE: CVE-2025-30160
CWE: CWE-400, CWE-502
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-g8vq-v3mg-7mrg
Type: github-advisory

## Affected
- crates.io: `redlib` — affected >=0 <0.36.0

## Details
A vulnerability has been identified in Redlib where an attacker can cause a denial-of-service (DOS) condition by submitting a specially crafted base2048-encoded DEFLATE decompression bomb to the restore_preferences form. This leads to excessive memory consumption and potential system instability, which can be exploited to disrupt Redlib instances. This vulnerability was introduced in 2e95e1fc6e2064ccfae87964b4860bda55eddb9a and fixed in 15147cea8e42f6569a11603d661d71122f6a02dc.

### Impact
_What kind of vulnerability is it? Who is impacted?_

This vulnerability allows a remote attacker with network access to exploit the preference restoration mechanism by providing a compressed payload that expands dramatically upon decompression. The issue arises because the system automatically decompresses user-supplied data without enforcing size limits, potentially leading to:

- Out-of-memory (OOM) conditions
- OS-level resource exhaustion, potentially leading to broader system instability or crashes
- Repeated exploitation, keeping the target system in a persistent degraded state
- Denial-of-service of any public instance

### Patches
The problem has been patched in 15147cea8e42f6569a11603d661d71122f6a02dc. Users should upgrade to v0.36.0.

### Workarounds
Until a patch is available, users can:

- Implement request size limits at the web server or application level to reject excessively large inputs.
- Disable or restrict the restore_preferences route (`/settings/encoded-restore`) at the reverse-proxy level if not required.
- Monitor server logs for unusually large or repeated restore_preferences requests and block offending IPs.

## References
- https://github.com/crewjam/saml/security/advisories/GHSA-5mqj-xc49-246p
- https://github.com/redlib-org/redlib/security/advisories/GHSA-g8vq-v3mg-7mrg
- https://nvd.nist.gov/vuln/detail/CVE-2025-30160
- https://github.com/redlib-org/redlib/commit/15147cea8e42f6569a11603d661d71122f6a02dc
- https://github.com/redlib-org/redlib/commit/2e95e1fc6e2064ccfae87964b4860bda55eddb9a
- https://github.com/redlib-org/redlib
