# [H] Fix failure to strip Authorization header on HTTP downgrade

## Summary
Severity: High
Advisory: GHSA-w248-ffj2-4v5q
CVE: CVE-2022-31043
CWE: CWE-200, CWE-212, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-w248-ffj2-4v5q
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=4.0.0 <6.5.7
- Packagist: `guzzlehttp/guzzle` — affected >=7.0.0 <7.4.4

## Details
### Impact

`Authorization` headers on requests are sensitive information. On making a request using the `https` scheme to a server which responds with a redirect to a URI with the `http` scheme, we should not forward the `Authorization` header on. This is much the same as to how we don't forward on the header if the host changes. Prior to this fix, `https` to `http` downgrades did not result in the `Authorization` header being removed, only changes to the host.

### Patches

Affected Guzzle 7 users should upgrade to Guzzle 7.4.4 as soon as possible. Affected users using any earlier series of Guzzle should upgrade to Guzzle 6.5.7 or 7.4.4.

### Workarounds

An alternative approach would be to use your own redirect middleware, rather than ours, if you are unable to upgrade. If you do not require or expect redirects to be followed, one should simply disable redirects all together.

### References

* [RFC9110 Section 15.4](https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx)

### For more information

If you have any questions or comments about this advisory, please get in touch with us in `#guzzle` on the [PHP HTTP Slack](https://php-http.slack.com/). Do not report additional security advisories in that public channel, however - please follow our [vulnerability reporting process](https://github.com/guzzle/guzzle/security/policy).

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-w248-ffj2-4v5q
- https://nvd.nist.gov/vuln/detail/CVE-2022-31043
- https://github.com/guzzle/guzzle/commit/e3ff079b22820c2029d4c2a87796b6a0b8716ad8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle/CVE-2022-31043.yaml
- https://github.com/guzzle/guzzle
- https://www.debian.org/security/2022/dsa-5246
- https://www.drupal.org/sa-core-2022-011
- https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx
