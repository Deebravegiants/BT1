# [H] vLLM vulnerable to Server-Side Request Forgery (SSRF) through MediaConnector

## Summary
Severity: High
Advisory: GHSA-qh4c-xf7m-gxfc
CVE: CVE-2026-24779
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-qh4c-xf7m-gxfc
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.14.1

## Details
### Summary
A Server-Side Request Forgery (SSRF) vulnerability exists in the `MediaConnector` class within the vLLM project's multimodal feature set. The load_from_url and load_from_url_async methods obtain and process media from URLs provided by users, using different Python parsing libraries when restricting the target host. These two parsing libraries have different interpretations of backslashes, which allows the host name restriction to be bypassed. This allows an attacker to coerce the vLLM server into making arbitrary requests to internal network resources.

This vulnerability is particularly critical in containerized environments like `llm-d`, where a compromised vLLM pod could be used to scan the internal network, interact with other pods, and potentially cause Denial of Service or access sensitive data. For example, an attacker could make the vLLM pod send malicious requests to an internal `llm-d` management endpoint, leading to system instability by falsely reporting metrics like the KV cache state.

### Details
The core of the vulnerability lies in the `MediaConnector.load_from_url` method and its asynchronous counterpart. These methods accept a URL string to fetch media content (images, audio, video).

>     def load_from_url(
>         self,
>         url: str,
>         media_io: MediaIO[_M],
>         *,
>         fetch_timeout: int | None = None,
>     ) -> _M:  # type: ignore[type-var]
>         url_spec = urlparse(url)
> 
>         if url_spec.scheme.startswith("http"):
>             self._assert_url_in_allowed_media_domains(url_spec)
> 
>             connection = self.connection
>             data = connection.get_bytes(
>                 url,
>                 timeout=fetch_timeout,
>                 allow_redirects=envs.VLLM_MEDIA_URL_ALLOW_REDIRECTS,
>             )
> 
>             return media_io.load_bytes(data)

The URL validation uses the `urlparse` function from Python's `urllib` module, while the request is made using the `request` function from Python's `requests` module. The `requests` module's underlying URL parsing is implemented using the `parse_url` function from Python's `urllib3`. These two parsing functions follow different URL specifications; one is implemented according to the RFC 3986 specification, and the other is implemented according to the WHATWG Living Standard. There is a difference in how the two functions handle backslashes (`\`) in URLs, which allows the hostname restriction to be bypassed.

### Fix

* https://github.com/vllm-project/vllm/pull/32746

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-qh4c-xf7m-gxfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24779
- https://github.com/vllm-project/vllm/pull/32746
- https://github.com/vllm-project/vllm/commit/f46d576c54fb8aeec5fc70560e850bed38ef17d7
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24779.json
- https://pypi.org/project/vllm
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2020.yaml
- https://github.com/advisories/GHSA-qh4c-xf7m-gxfc
- https://bugzilla.redhat.com/show_bug.cgi?id=2433624
- https://access.redhat.com/security/cve/CVE-2026-24779
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/errata/RHSA-2026:3782
- https://access.redhat.com/errata/RHSA-2026:3462
- https://access.redhat.com/errata/RHSA-2026:3461
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/errata/RHSA-2026:30088
- https://access.redhat.com/errata/RHSA-2026:30087
- https://access.redhat.com/errata/RHSA-2026:19712
- https://access.redhat.com/errata/RHSA-2026:10184
