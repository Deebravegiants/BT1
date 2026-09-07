# [M] Unencrypted storage of client side sessions

## Summary
Severity: Medium
Advisory: GHSA-phj8-4cq3-794g
CVE: CVE-2021-29481
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-phj8-4cq3-794g
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-session` — affected >=0 <1.9.0

## Details
### Impact

The default configuration of client side sessions results in unencrypted, but signed, data being set as cookie values. This means that if something sensitive goes into the session, it could be read by something with access to the cookies.

Note: the documentation does point this out and encourage users to add an encryption key, but it is not mandatory.

For this to be a vulnerability, some kind of sensitive data would need to be stored in the session and the session cookie would have to leak. For example, the cookies are not configured with httpOnly and an adjacent XSS vulnerability within the site allowed capture of the cookies.

The proposed change is to change the default behaviour to use a randomly generated encryption key. This would mean that sessions do not survive app restarts, but this is already the behaviour given the random signing key.

### Patches

As of version 1.9.0, a securely randomly generated signing key is used.

### Workarounds

Supply an encryption key, as per the documentation recommendation.

### References

- https://github.com/ratpack/ratpack/pull/1590

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-phj8-4cq3-794g
- https://nvd.nist.gov/vuln/detail/CVE-2021-29481
- https://github.com/ratpack/ratpack/pull/1590
- https://github.com/ratpack/ratpack
