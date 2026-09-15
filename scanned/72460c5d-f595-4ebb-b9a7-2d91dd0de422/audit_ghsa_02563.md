# [C] Lacking Protection against HTTP Request Smuggling in mitmproxy

## Summary
Severity: Critical
Advisory: GHSA-22gh-3r9q-xf38
CVE: CVE-2021-39214
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-22gh-3r9q-xf38
Type: github-advisory

## Affected
- PyPI: `mitmproxy` — affected >=0 <7.0.3

## Details
### Impact

In mitmproxy 7.0.2 and below, a malicious client or server is able to perform [HTTP request smuggling](https://en.wikipedia.org/wiki/HTTP_request_smuggling) attacks through mitmproxy. This means that a malicious client/server could smuggle a request/response through mitmproxy as part of another request/response's HTTP message body. While mitmproxy would only see one request, the target server would see multiple requests. A smuggled request is still captured as part of another request's body, but it does not appear in the request list and does not go through the usual mitmproxy event hooks, where users may have implemented custom access control checks or input sanitization.

Unless you use mitmproxy to protect an HTTP/1 service, no action is required.


### Patches

The vulnerability has been fixed in mitmproxy 7.0.3 and above.


### Acknowledgements

We thank João Sobral (@chinchila) for responsibly disclosing this vulnerability to the mitmproxy team.


### Timeline

- **2021-09-08**: Received initial report for mitmproxy <= 6.0.2.
- **2021-09-08**: Requested clarification if 7.x is affected.
- **2021-09-10**: Received additional details, 7.x situation still unclear.
- **2021-09-13**: Internally determined that 7.x is also affected.
- **2021-09-13**: Shared initial fix with researcher.
- **2021-09-14**: Received confirmation that fix is working, but H2.TE/H2.CL should also be looked at.
- **2021-09-14**: Shared revised fix that includes additional H2.TE mitigations.
- **2021-09-14**: Received confirmation that revised fix is working.
- **2021-09-16**: Completed internal patch review.
- **2021-09-16**: Published patch release and advisory.

## References
- https://github.com/mitmproxy/mitmproxy/security/advisories/GHSA-22gh-3r9q-xf38
- https://nvd.nist.gov/vuln/detail/CVE-2021-39214
- https://github.com/mitmproxy/mitmproxy
- https://github.com/pypa/advisory-database/tree/main/vulns/mitmproxy/PYSEC-2021-328.yaml
