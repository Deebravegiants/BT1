# [H] Failure to strip the Cookie header on change in host or HTTP downgrade

## Summary
Severity: High
Advisory: GHSA-f2wf-25xc-69c9
CVE: CVE-2022-31042
CWE: CWE-200, CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-f2wf-25xc-69c9
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=4.0.0 <6.5.7
- Packagist: `guzzlehttp/guzzle` — affected >=7.0.0 <7.4.4

## Details
### Impact

`Cookie` headers on requests are sensitive information. On making a request using the `https` scheme to a server which responds with a redirect to a URI with the `http` scheme, or on making a request to a server which responds with a redirect to a a URI to a different host, we should not forward the `Cookie` header on. Prior to this fix, only cookies that were managed by our cookie middleware would be safely removed, and any `Cookie` header manually added to the initial request would not be stripped. We now always strip it, and allow the cookie middleware to re-add any cookies that it deems should be there.

### Patches

Affected Guzzle 7 users should upgrade to Guzzle 7.4.4 as soon as possible. Affected users using any earlier series of Guzzle should upgrade to Guzzle 6.5.7 or 7.4.4.

### Workarounds

An alternative approach would be to use your own redirect middleware, rather than ours, if you are unable to upgrade. If you do not require or expect redirects to be followed, one should simply disable redirects all together.

### References

* [RFC9110 Section 15.4](https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx)

### For more information

If you have any questions or comments about this advisory, please get in touch with us in `#guzzle` on the [PHP HTTP Slack](https://php-http.slack.com/). Do not report additional security advisories in that public channel, however - please follow our [vulnerability reporting process](https://github.com/guzzle/guzzle/security/policy).

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-f2wf-25xc-69c9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31042
- https://github.com/guzzle/guzzle/commit/e3ff079b22820c2029d4c2a87796b6a0b8716ad8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle/CVE-2022-31042.yaml
- https://github.com/guzzle/guzzle
- https://www.debian.org/security/2022/dsa-5246
- https://www.drupal.org/sa-core-2022-011
- https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx
