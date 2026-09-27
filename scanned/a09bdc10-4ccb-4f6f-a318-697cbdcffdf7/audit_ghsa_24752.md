# [H] Cross-domain cookie leakage in Guzzle

## Summary
Severity: High
Advisory: GHSA-cwmx-hcrq-mhc3
CVE: CVE-2022-29248
CWE: CWE-200, CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-cwmx-hcrq-mhc3
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/guzzle` — affected >=0 <6.5.6
- Packagist: `guzzlehttp/guzzle` — affected >=7.0.0 <7.4.3

## Details
### Impact

Previous version of Guzzle contain a vulnerability with the cookie middleware. The vulnerability is that it is not checked if the cookie domain equals the domain of the server which sets the cookie via the `Set-Cookie` header, allowing a malicious server to set cookies for unrelated domains. For example an attacker at `www.example.com` might set a session cookie for `api.example.net`, logging the Guzzle client into their account and retrieving private API requests from the security log of their account.

Note that our cookie middleware is disabled by default, so most library consumers will not be affected by this issue. Only those who manually add the cookie middleware to the handler stack or construct the client with `['cookies' => true]` are affected. Moreover, those who do not use the same Guzzle client to call multiple domains and have disabled redirect forwarding are not affected by this vulnerability.

### Patches

Affected Guzzle 7 users should upgrade to Guzzle 7.4.3 as soon as possible. Affected users using any earlier series of Guzzle should upgrade to Guzzle 6.5.6 or 7.4.3.

### Workarounds

If you do not need support for cookies, turn off the cookie middleware. It is already off by default, but if you have turned it on and no longer need it, turn it off.

### References

* [RFC6265 Section 5.3](https://datatracker.ietf.org/doc/html/rfc6265#section-5.3)
* [RFC9110 Section 15.4](https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx)

### For more information

If you have any questions or comments about this advisory, please get in touch with us in `#guzzle` on the [PHP HTTP Slack](https://php-http.slack.com/). Do not report additional security advisories in that public channel, however - please follow our [vulnerability reporting process](https://github.com/guzzle/guzzle/security/policy).

## References
- https://github.com/guzzle/guzzle/security/advisories/GHSA-cwmx-hcrq-mhc3
- https://nvd.nist.gov/vuln/detail/CVE-2022-29248
- https://github.com/guzzle/guzzle/pull/3018
- https://github.com/guzzle/guzzle/commit/74a8602c6faec9ef74b7a9391ac82c5e65b1cdab
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/guzzle/CVE-2022-29248.yaml
- https://github.com/guzzle/guzzle
- https://www.debian.org/security/2022/dsa-5246
- https://www.drupal.org/sa-core-2022-010
