# [H] Rancher API Server Cross-site Scripting Vulnerability

## Summary
Severity: High
Advisory: GHSA-833m-37f7-jq55
CVE: CVE-2023-32192
CWE: CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-833m-37f7-jq55
Type: github-advisory

## Affected
- Go: `github.com/rancher/apiserver` — affected >=0 <0.0.0-20240207153957-4fd7d821d952

## Details
### Impact
A vulnerability has been identified in which unauthenticated cross-site scripting (XSS) in the API Server's public API endpoint can be exploited. This can lead to an attacker exploiting the vulnerability to trigger JavaScript code and execute commands remotely. 

The attack vector was identified as a Reflected XSS.

API Server propagates malicious payloads from user input to the UI, which renders the output. For example, a malicious URL gets rendered into a script that is executed on a page.

The changes addressed by this fix are:
- Encode input that comes from the request URL before adding it to the response.
- The request input is escaped by changing the URL construction that is used for links to use `url.URL`.
- The request input is escaped by escaping the JavaScript and CSS variables with attribute encoding as defined by [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#output-encoding-rules-summary).

### Patches
Patched versions include the following commits:

| Branch    | Commit |
| -------- | ------- |
| master  | 4fd7d82 |
| release/v2.8 | 69b3c2b |
| release/v2.8.s3 | a3b9e37 |
| release/v2.7 | 4e102cf |
| release/v2.7.s3 | 97a10a3 |
| release/v2.6 | 4df268e |

### Workarounds
There is no direct mitigation besides updating API Server to a patched version.

### References
If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security-related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/apiserver/security/advisories/GHSA-833m-37f7-jq55
- https://nvd.nist.gov/vuln/detail/CVE-2023-32192
- https://github.com/rancher/apiserver/commit/4df268e250f625fa323349062636496e0aeff4e4
- https://github.com/rancher/apiserver/commit/4e102cf0d07b1af3d10d82c3e5a751a869b8a6c7
- https://github.com/rancher/apiserver/commit/4fd7d821d952510bfe38c9d4a3e2a65157f50525
- https://github.com/rancher/apiserver/commit/69b3c2b56f3fa5a421889c533dada8cd08783cda
- https://github.com/rancher/apiserver/commit/97a10a30200cb851afd8ee85ee6b2295c4b6e5ee
- https://github.com/rancher/apiserver/commit/a3b9e3721c1b558ee63aec9594e37c223a5c8437
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32192
- https://github.com/rancher/apiserver
