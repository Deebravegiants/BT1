# [C] Potential leak of authentication data to 3rd parties

## Summary
Severity: Critical
Advisory: GHSA-558p-m34m-vpmq
CVE: CVE-2023-30846
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-558p-m34m-vpmq
Type: github-advisory

## Affected
- npm: `typed-rest-client` — affected >=0 <1.8.0

## Details
### Impact
Users of typed-rest-client library version 1.7.3 or lower are vulnerable to leak authentication data to 3rd parties. 

The flow of the vulnerability is as follows:

1. Send any request with `BasicCredentialHandler`, `BearerCredentialHandler` or `PersonalAccessTokenCredentialHandler` 
2. The target host may return a redirection (3xx), with a link to a second host.
3. The next request will use the credentials to authenticate with the second host, by setting the `Authorization` header.

The expected behavior is that the next request will *NOT* set the `Authorization` header.


### Patches
The problem was fixed on April 1st 2020.


### Workarounds
There is no workaround.

### References
This is similar to the following issues in nature:
1. [HTTP authentication leak in redirects](https://curl.haxx.se/docs/CVE-2018-1000007.html) - I used the same solution as CURL did.
2. [CVE-2018-1000007](https://nvd.nist.gov/vuln/detail/CVE-2018-1000007).

## References
- https://github.com/microsoft/typed-rest-client/security/advisories/GHSA-558p-m34m-vpmq
- https://nvd.nist.gov/vuln/detail/CVE-2023-30846
- https://github.com/microsoft/typed-rest-client/pull/207
- https://github.com/microsoft/typed-rest-client/commit/f9ff755631b982ee1303dfc3e3c823d0d31233e8
- https://github.com/microsoft/typed-rest-client
- https://security.netapp.com/advisory/ntap-20230601-0008
