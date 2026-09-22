# [C] vLLM: OpenAI auth bypass

## Summary
Severity: Critical
Advisory: GHSA-94f4-hr76-p5j6
CVE: CVE-2026-48746
CWE: CWE-444, CWE-501
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-94f4-hr76-p5j6
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.3.0 <0.22.0

## Details
### Summary

A vulnerability in ASGI web servers and starlette's trust on those web servers enables an authentication bypass of the OpenAI API `AuthenticationMiddleware`, which was discovered during @x41sec's source code audit.
It allows to use the API without providing the configured `VLLM_API_KEY` or `--api-key`.

### Details

In https://github.com/vllm-project/vllm/blob/v0.14.0/vllm/entrypoints/openai/api_server.py#L689-L692 the `url_path` is taken from the `URL`, which is reconstructed by _starlette_ based on the request `scope`.

```py
from starlette.datastructures import URL, Headers, MutableHeaders, State

# ...

url_path = URL(scope=scope).path.removeprefix(root_path)
headers = Headers(scope=scope)
if url_path.startswith("/v1") and not self.verify_token(headers):
    response = JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    return response(scope, receive, send)
return self.app(scope, receive, send)
```

The request `scope` includes the request's `Host:` header and reconstructs the URL as shown below:

```py
f"{scheme}://{host_header}{path}"
```

Neither starlette nor [any of the ASGI servers](https://asgi.readthedocs.io/en/latest/implementations.html#servers) (including uvicorn, which vllm uses) properly filter the `Host:` header for invalid characters. This allows an attacker to include special URL characters such as `/` or `?` in the `Host:` header and thereby control the reconstructed URL and it's `.path` attribute.

FastAPI/starlette's routing uses the HTTP path and does not depend on the parsed url.path attribute, allowing attackers to reach an endpoint via a certain path while providing a different value in the `.path`.

### Impact
- Instances of vllm that use an API Key for the OpenAI API and expose the API to attackers.
- Instances behind an RFC-conforming web server (such as nginx) are **not** affected.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-94f4-hr76-p5j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48746
- https://github.com/vllm-project/vllm/pull/43426
- https://x41-dsec.de/lab/advisories/x41-2026-002-starlette
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48746.json
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-226.yaml
- https://bugzilla.redhat.com/show_bug.cgi?id=2491581
- https://access.redhat.com/security/cve/CVE-2026-48746
- https://access.redhat.com/errata/RHSA-2026:61629
- https://access.redhat.com/errata/RHSA-2026:61627
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/errata/RHSA-2026:42142
- https://access.redhat.com/errata/RHSA-2026:42132
- https://access.redhat.com/errata/RHSA-2026:36006
- https://access.redhat.com/errata/RHSA-2026:36005
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/errata/RHSA-2026:30088
