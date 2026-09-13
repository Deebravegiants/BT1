# [M] mitmproxy has an LDAP Injection

## Summary
Severity: Medium
Advisory: GHSA-527g-3w9m-29hv
CVE: CVE-2026-40606
CWE: CWE-90
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-527g-3w9m-29hv
Type: github-advisory

## Affected
- PyPI: `mitmproxy` — affected >=0 <12.2.2

## Details
### Impact
In mitmproxy 12.2.1 and below, the builtin LDAP proxy authentication does not correctly sanitize the username when querying the LDAP server. This allows a malicious client to bypass authentication.

Only mitmproxy instances using the `proxyauth` option with LDAP are affected. This option is not enabled by default.

### Patches

The vulnerability has been fixed in mitmproxy 12.2.2 and above.

### Acknowledgements

We thank Yue (Knox) Liu (@yueyueL) for responsibly disclosing this vulnerability to the mitmproxy team.

### Timeline

- **2025-12-08**: Received initial report. 
- **2025-12-09**: Verified report and confirmed receipt.
- **2026-01-02**: Informed researcher that patch will be part of the next regular patch release.
- **2026-04-12**: Published patch release and advisory.

## References
- https://github.com/mitmproxy/mitmproxy/security/advisories/GHSA-527g-3w9m-29hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40606
- https://github.com/mitmproxy/mitmproxy
- https://github.com/pypa/advisory-database/tree/main/vulns/mitmproxy/PYSEC-2026-92.yaml
