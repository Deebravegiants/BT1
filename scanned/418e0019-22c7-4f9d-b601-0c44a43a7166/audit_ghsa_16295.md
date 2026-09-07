# [H] Norman API Cross-site Scripting Vulnerability

## Summary
Severity: High
Advisory: GHSA-r8f4-hv23-6qp6
CVE: CVE-2023-32193
CWE: CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-r8f4-hv23-6qp6
Type: github-advisory

## Affected
- Go: `github.com/rancher/norman` — affected >=0 <0.0.0-20240207153100-3bb70b772b52

## Details
### Impact
A vulnerability has been identified in which unauthenticated cross-site scripting (XSS) in Norman's public API endpoint can be exploited. This can lead to an attacker exploiting the vulnerability to trigger JavaScript code and execute commands remotely. 

The attack vector was identified as a Reflected XSS.

Norman API propagates malicious payloads from user input to the UI, which renders the output. For example, a malicious URL gets rendered into a script that is executed on a page.

The changes addressed by this fix are:
- Encode input that comes from the request URL before adding it to the response.
- The request input is escaped by changing the URL construction that is used for links to use `url.URL`.
- The request input is escaped by escaping the JavaScript and CSS variables with attribute encoding as defined by [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#output-encoding-rules-summary).

### Patches
Patched versions include the following commits:

| Branch    | Commit |
| -------- | ------- |
| master  | 3bb70b7 |
| release/v2.8 | a6a6cf5 |
| release/v2.7 | cb54924 |
| release/v2.7.s3 | 7b2b467 |
| release/v2.6 | bd13c65 |

### Workarounds
There is no direct mitigation besides updating Norman API to a patched version.

### References
If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security-related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/norman/security/advisories/GHSA-r8f4-hv23-6qp6
- https://nvd.nist.gov/vuln/detail/CVE-2023-32193
- https://github.com/rancher/norman/commit/3bb70b772b52297feac64f5fdeb1b13c06c37e39
- https://github.com/rancher/norman/commit/7b2b467995e6dfab6d4a5dee8dffc15033ae8269
- https://github.com/rancher/norman/commit/a6a6cf5696088c32002953d36b75bdcc84f2399e
- https://github.com/rancher/norman/commit/bd13c653293b9b5e0b37e8a6ccd1c3277f4623ed
- https://github.com/rancher/norman/commit/cb54924f25c7666511a913cd41834299ef22dba4
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32193
- https://github.com/rancher/norman
