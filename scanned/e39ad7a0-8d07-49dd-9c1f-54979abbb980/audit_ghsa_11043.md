# [M] Quill vulnerable to SSRF via unvalidated URL from Apple notarization log retrieval

## Summary
Severity: Medium
Advisory: GHSA-7q3q-5px6-4c5p
CVE: CVE-2026-31959
CWE: CWE-20, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7q3q-5px6-4c5p
Type: github-advisory

## Affected
- Go: `github.com/anchore/quill` — affected >=0 <0.7.1

## Details
### Impact

Quill before version `v0.7.1` contains a Server-Side Request Forgery (SSRF) vulnerability when attempting to fetch the Apple notarization submission logs. Exploitation requires the ability to modify API responses from Apple's notarization service, which is not possible under standard network conditions due to HTTPS with proper TLS certificate validation; however, environments with TLS-intercepting proxies (common in corporate networks), compromised certificate authorities, or other trust boundary violations are at risk.

When retrieving submission logs, Quill fetches a URL provided in the API response without validating that the scheme is https or that the host does not point to a local or multicast IP address. An attacker who can tamper with the response can supply an arbitrary URL, causing the Quill client to issue HTTP or HTTPS requests to attacker-controlled or internal network destinations. This could lead to exfiltration of sensitive data such as cloud provider credentials or internal service responses. Both the Quill CLI and library are affected when used to retrieve notarization submission logs.


### Patches

Fixed in Quill version `v0.7.1`


### Workarounds

None

### Credit

Anchore would like to thank opera-aklajn (Opera) for reporting this vulnerability

### Resources

- [Apple Get Submission Log API Documentation](https://developer.apple.com/documentation/notaryapi/get-submission-log)

## References
- https://github.com/anchore/quill/security/advisories/GHSA-7q3q-5px6-4c5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-31959
- https://github.com/anchore/quill/commit/e41d66a517c2dc20ad8e9fbccffbdc6ba5ef0020
- https://developer.apple.com/documentation/notaryapi/get-submission-log
- https://github.com/anchore/quill
- https://github.com/anchore/quill/releases/tag/v0.7.1
