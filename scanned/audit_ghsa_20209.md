# [H] Change in port should be considered a change in origin

## Summary
Severity: High
Advisory: GHSA-q559-8m2m-g699
CVE: CVE-2022-31091
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-q559-8m2m-g699
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <6.5.8
- Packagist: `guzzlehttp/guzzle` — affected >=7.0.0 <7.4.5

## Details
### Impact

`Authorization` and `Cookie` headers on requests are sensitive information. On making a request which responds with a redirect to a URI with a different port, if we choose to follow it, we should remove the `Authorization` and `Cookie` headers from the request, before containing. Previously, we would only consider a change in host or scheme downgrade. Now, we consider any change in host, port or scheme to be a change in origin.

### Patches

Affected Guzzle 7 users should upgrade to Guzzle 7.4.5 as soon as possible. Affected users using any earlier series of Guzzle should upgrade to Guzzle 6.5.8 or 7.4.5.

### Workarounds

An alternative approach would be to use your own redirect middleware, rather than ours, if you are unable to upgrade. If you do not require or expect redirects to be followed, one should simply disable redirects all together.

### References

* [RFC9110 Section 15.4](https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx)
* [CVE-2022-27776](https://curl.se/docs/CVE-2022-27776.html)

### For more information

If you have any questions or comments about this advisory, please get in touch with us in `#guzzle` on the [PHP HTTP Slack](https://php-http.slack.com/). Do not report additional security advisories in that public channel, however please follow our [vulnerability reporting process](https://github.com/guzzle/guzzle/security/policy).

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-q559-8m2m-g699
- https://nvd.nist.gov/vuln/detail/CVE-2022-31091
- https://github.com/guzzle/guzzle/commit/1dd98b0564cb3f6bd16ce683cb755f94c10fbd82
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle/CVE-2022-31091.yaml
- https://github.com/guzzle/guzzle
- https://security.gentoo.org/glsa/202305-24
- https://www.debian.org/security/2022/dsa-5246
