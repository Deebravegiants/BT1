# [M] docling-graph has SSRF via Missing Internal IP Validation in URLInputHandler

## Summary
Severity: Medium
Advisory: GHSA-fqph-j6v6-jvgx
CVE: CVE-2026-44520
CWE: CWE-601, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-fqph-j6v6-jvgx
Type: github-advisory

## Affected
- PyPI: `docling-graph` — affected >=0 <1.5.1

## Details
### Impact

The `URLInputHandler` class in `docling_graph/core/input/handlers.py` makes HTTP requests to user-supplied URLs without validating whether the target resolves to a private, loopback, or link-local IP address. The `URLValidator` only checks for a valid scheme and non-empty `netloc`, performing no IP-level validation. Additionally, `requests.head()` was called with `allow_redirects=True`, allowing an attacker to redirect requests to internal endpoints via an intermediary URL.

An attacker who can control the `--source` CLI argument or `PipelineConfig.source` API parameter can trigger Server-Side Request Forgery (SSRF) to reach:
- Cloud metadata endpoints (e.g. `169.254.169.254`) to steal IAM credentials
- Internal services on loopback (`127.0.0.1`) or private network ranges (`10.x`, `172.16.x`, `192.168.x`)

This affects deployments where `docling-graph` processes URLs from untrusted input, such as multi-tenant pipelines or server-side automation.

### Patches

The vulnerability is fixed in **v1.5.1**.

Users should upgrade immediately:
```
pip install --upgrade docling-graph
```

The fix adds IP validation via `ipaddress` and `socket.gethostbyname()` before any request is made, blocks private/loopback/link-local/reserved addresses, and disables redirect following (`allow_redirects=False`) with explicit validation of any `Location` header before following it.

### Workarounds

If upgrading is not immediately possible, ensure that **all URLs passed to `URLInputHandler` come exclusively from trusted, internal sources**, never from user-supplied or external input. There is no safe code-level workaround short of applying the patch, as the vulnerability is in the library itself.

### Resources

- [CWE-918: Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [AWS Instance Metadata endpoint](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)

## References
- https://github.com/docling-project/docling-graph/security/advisories/GHSA-fqph-j6v6-jvgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44520
- https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- https://github.com/docling-project/docling-graph
