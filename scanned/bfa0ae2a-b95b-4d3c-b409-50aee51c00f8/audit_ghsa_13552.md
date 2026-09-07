# [M] urllib3's request body not stripped after redirect from 303 status changes request method to GET

## Summary
Severity: Medium
Advisory: GHSA-g4mx-q9vg-27p4
CVE: CVE-2023-45803
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-g4mx-q9vg-27p4
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=2.0.0 <2.0.7
- PyPI: `urllib3` — affected >=0 <1.26.18

## Details
urllib3 previously wouldn't remove the HTTP request body when an HTTP redirect response using status 303 "See Other" after the request had its method changed from one that could accept a request body (like `POST`) to `GET` as is required by HTTP RFCs. Although the behavior of removing the request body is not specified in the section for redirects, it can be inferred by piecing together information from different sections and we have observed the behavior in other major HTTP client implementations like curl and web browsers.

From [RFC 9110 Section 9.3.1](https://www.rfc-editor.org/rfc/rfc9110.html#name-get):

> A client SHOULD NOT generate content in a GET request unless it is made directly to an origin server that has previously indicated, in or out of band, that such a request has a purpose and will be adequately supported.

## Affected usages

Because the vulnerability requires a previously trusted service to become compromised in order to have an impact on confidentiality we believe the exploitability of this vulnerability is low. Additionally, many users aren't putting sensitive data in HTTP request bodies, if this is the case then this vulnerability isn't exploitable.

Both of the following conditions must be true to be affected by this vulnerability:

* If you're using urllib3 and submitting sensitive information in the HTTP request body (such as form data or JSON)
* The origin service is compromised and starts redirecting using 303 to a malicious peer or the redirected-to service becomes compromised.

## Remediation

You can remediate this vulnerability with any of the following steps:

* Upgrade to a patched version of urllib3 (v1.26.18 or v2.0.7)
* Disable redirects for services that you aren't expecting to respond with redirects with `redirects=False`.
* Disable automatic redirects with `redirects=False` and handle 303 redirects manually by stripping the HTTP request body.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-g4mx-q9vg-27p4
- https://nvd.nist.gov/vuln/detail/CVE-2023-45803
- https://github.com/urllib3/urllib3/commit/4e50fbc5db74e32cabd5ccc1ab81fc103adfe0b3
- https://github.com/urllib3/urllib3/commit/4e98d57809dacab1cbe625fddeec1a290c478ea9
- https://github.com/urllib3/urllib3/commit/b594c5ceaca38e1ac215f916538fb128e3526a36
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2023-212.yaml
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/releases/tag/1.26.18
- https://github.com/urllib3/urllib3/releases/tag/2.0.7
- https://lists.debian.org/debian-lts-announce/2024/12/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4R2Y5XK3WALSR3FNAGN7JBYV2B343ZKB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5F5CUBAN5XMEBVBZPHFITBLMJV5FIJJ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PPDPLM6UUMN55ESPQWJFLLIZY4ZKCNRX
- https://www.rfc-editor.org/rfc/rfc9110.html#name-get
