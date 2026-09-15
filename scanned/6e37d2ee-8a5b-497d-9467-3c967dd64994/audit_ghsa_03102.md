# [H] Insufficient Session Expiration in Kiali

## Summary
Severity: High
Advisory: GHSA-465w-gg5p-85c9
CVE: CVE-2020-1762
CWE: CWE-295, CWE-384, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-465w-gg5p-85c9
Type: github-advisory

## Affected
- Go: `github.com/kiali/kiali` — affected >=0.4.0 <1.15.1

## Details
An insufficient JWT validation vulnerability was found in Kiali versions 0.4.0 to 1.15.0 and was fixed in Kiali version 1.15.1, wherein a remote attacker could abuse this flaw by stealing a valid JWT cookie and using that to spoof a user session, possibly gaining privileges to view and alter the Istio configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1762
- https://github.com/kiali/kiali/commit/93f5cd0b6698e8fe8772afb8f35816f6c086aef1
- https://github.com/kiali/kiali/commit/c91a0949683976f621cca213c1193831d63b381c
- https://bugzilla.redhat.com/show_bug.cgi?id=1810387
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1762
- https://kiali.io/news/security-bulletins/kiali-security-001
