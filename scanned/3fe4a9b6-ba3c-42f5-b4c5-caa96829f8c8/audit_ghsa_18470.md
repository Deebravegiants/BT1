# [H] Cadwyn vulnerable to XSS on the docs page

## Summary
Severity: High
Advisory: GHSA-2gxp-6r36-m97r
CVE: CVE-2025-53528
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-2gxp-6r36-m97r
Type: github-advisory

## Affected
- PyPI: `cadwyn` — affected >=0 <5.4.3

## Details
### Summary
The `version` parameter of the `/docs` endpoint is vulnerable to a Reflected XSS (Cross-Site Scripting) attack.

### PoC
1. Setup a minimal app following the quickstart guide: https://docs.cadwyn.dev/quickstart/setup/
2. Click on the following PoC link: http://localhost:8000/docs?version=%27%2balert(document.domain)%2b%27

### Impact
Refer to this [security advisory](https://github.com/Visionatrix/Visionatrix/security/advisories/GHSA-w36r-9jvx-q48v) for an example of the impact of a similar vulnerability that shares the same root cause.

This XSS would notably allow an attacker to execute JavaScript code on a user's session for any application based on `Cadwyn` via a one-click attack.

A CVSS for the average case may be: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L

### Details
The vulnerable code snippet can be found in the 2 functions `swagger_dashboard` and `redoc_dashboard`: https://github.com/zmievsa/cadwyn/blob/main/cadwyn/applications.py#L387-L413

The implementation uses the [get_swagger_ui_html](https://fastapi.tiangolo.com/reference/openapi/docs/?h=get_swagger_ui_html#fastapi.openapi.docs.get_swagger_ui_html) function from FastAPI. This function does not encode or sanitize its arguments before using them to generate the HTML for the swagger documentation page and is not intended to be used with user-controlled arguments.

```python
    async def swagger_dashboard(self, req: Request) -> Response:
        version = req.query_params.get("version")

        if version:
            root_path = self._extract_root_path(req)
            openapi_url = root_path + f"{self.openapi_url}?version={version}"
            oauth2_redirect_url = self.swagger_ui_oauth2_redirect_url
            if oauth2_redirect_url:
                oauth2_redirect_url = root_path + oauth2_redirect_url
            return get_swagger_ui_html(
                openapi_url=openapi_url,
                title=f"{self.title} - Swagger UI",
                oauth2_redirect_url=oauth2_redirect_url,
                init_oauth=self.swagger_ui_init_oauth,
                swagger_ui_parameters=self.swagger_ui_parameters,
            )
        return self._render_docs_dashboard(req, cast("str", self.docs_url))
```

In this case, the `openapi_url` variable contains the version which comes from a user supplied query string without encoding or sanitisation. The user controlled injection ends up inside of a string in a `<script>` tag context: https://github.com/fastapi/fastapi/blob/master/fastapi/openapi/docs.py#L132

```python
    f"""
    ...
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """
```

By simply injecting a single quote we can escape from the string context and execute JavaScript like so `'+alert(document.domain)+'`

The resulting HTML sent back from the server contains the following injection:

```python
  const ui = SwaggerUIBundle({
        url: '/openapi/flows.json?flows='+alert(document.domain)+'',
```

## References
- https://github.com/zmievsa/cadwyn/security/advisories/GHSA-2gxp-6r36-m97r
- https://nvd.nist.gov/vuln/detail/CVE-2025-53528
- https://github.com/zmievsa/cadwyn/commit/b424ecd57cd8dabbc8fe39b8f8ccafea629c7728
- https://github.com/pypa/advisory-database/tree/main/vulns/cadwyn/PYSEC-2025-71.yaml
- https://github.com/zmievsa/cadwyn
- https://github.com/zmievsa/cadwyn/blob/5.4.3/CHANGELOG.md#543
