# [M] vLLM: Server-Side Request Forgery (SSRF) in `download_bytes_from_url `

## Summary
Severity: Medium
Advisory: GHSA-pf3h-qjgv-vcpr
CVE: CVE-2026-34753
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-pf3h-qjgv-vcpr
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.16.0 <0.19.0

## Details
### Summary

A Server Side Request Forgery (SSRF) vulnerability in `download_bytes_from_url` allows any actor who can control batch input JSON to make the vLLM batch runner issue arbitrary HTTP/HTTPS requests from the server, without any URL validation or domain restrictions.

This can be used to target internal services (e.g. cloud metadata endpoints or internal HTTP APIs) reachable from the vLLM host.

------

### Details

#### Vulnerable component

The vulnerable logic is in the batch runner entrypoint `vllm/entrypoints/openai/run_batch.py`, function `download_bytes_from_url`:

```
# run_batch.py Lines 442-482
async def download_bytes_from_url(url: str) -> bytes:
    """
    Download data from a URL or decode from a data URL.

    Args:
        url: Either an HTTP/HTTPS URL or a data URL (data:...;base64,...)

    Returns:
        Data as bytes
    """
    parsed = urlparse(url)

    # Handle data URLs (base64 encoded)
    if parsed.scheme == "data":
        # Format: data:...;base64,<base64_data>
        if "," in url:
            header, data = url.split(",", 1)
            if "base64" in header:
                return base64.b64decode(data)
            else:
                raise ValueError(f"Unsupported data URL encoding: {header}")
        else:
            raise ValueError(f"Invalid data URL format: {url}")

    # Handle HTTP/HTTPS URLs
    elif parsed.scheme in ("http", "https"):
        async with (
            aiohttp.ClientSession() as session,
            session.get(url) as resp,
        ):
            if resp.status != 200:
                raise Exception(
                    f"Failed to download data from URL: {url}. Status: {resp.status}"
                )
            return await resp.read()

    else:
        raise ValueError(
            f"Unsupported URL scheme: {parsed.scheme}. "
            "Supported schemes: http, https, data"
        )
```

Key properties:

- The function only parses the URL to dispatch on the scheme (`data`, `http`, `https`).
- For `http` / `https`, it directly calls `session.get(url)` on the provided string.
- There is no validation of:
  - hostname or IP address,
  - whether the target is internal or external,
  - port number,
  - path, query, or redirect target.
- This is in contrast to the multimodal media path (`MediaConnector`), which implements an explicit domain allowlist. `download_bytes_from_url` does not reuse that protection.

#### URL controllability

The `url` argument is fully controlled by batch input JSON via the `file_url` field of `BatchTranscriptionRequest` / `BatchTranslationRequest`.

1. Batch request body type:

```
# run_batch.py Line 67-80
class BatchTranscriptionRequest(TranscriptionRequest):
    """
    Batch transcription request that uses file_url instead of file.

    This class extends TranscriptionRequest but replaces the file field
    with file_url to support batch processing from audio files written in JSON format.
    """

    file_url: str = Field(
        ...,
        description=(
            "Either a URL of the audio or a data URL with base64 encoded audio data. "
        ),
    )
```

```
# run_batch.py Line 98-111
class BatchTranslationRequest(TranslationRequest):
    """
    Batch translation request that uses file_url instead of file.

    This class extends TranslationRequest but replaces the file field
    with file_url to support batch processing from audio files written in JSON format.
    """

    file_url: str = Field(
        ...,
        description=(
            "Either a URL of the audio or a data URL with base64 encoded audio data. "
        ),
    )
```

There is no restriction on the domain, IP, or port of `file_url` in these models.

1. Batch input is parsed directly from the batch file:

```
# run_batch.py Line 139-179
class BatchRequestInput(OpenAIBaseModel):
    ...
    url: str
    body: BatchRequestInputBody
    @field_validator("body", mode="plain")
    @classmethod
    def check_type_for_url(cls, value: Any, info: ValidationInfo):
        url: str = info.data["url"]
        ...
        if url == "/v1/audio/transcriptions":
            return BatchTranscriptionRequest.model_validate(value)
        if url == "/v1/audio/translations":
            return BatchTranslationRequest.model_validate(value)
```

```
# run_batch.py Line 770-781
   logger.info("Reading batch from %s...", args.input_file)

    # Submit all requests in the file to the engine "concurrently".
    response_futures: list[Awaitable[BatchRequestOutput]] = []
    for request_json in (await read_file(args.input_file)).strip().split("\n"):
        # Skip empty lines.
        request_json = request_json.strip()
        if not request_json:
            continue

        request = BatchRequestInput.model_validate_json(request_json)
```

The batch runner reads each line of the input file (`args.input_file`), parses it as JSON, and constructs a `BatchTranscriptionRequest` / `BatchTranslationRequest`. Whatever `file_url` appears in that JSON line becomes `batch_request_body.file_url`.

1. `file_url` is passed directly into `download_bytes_from_url`:

```
# run_batch.py Line 610-623
def wrapper(handler_fn: Callable):
        async def transcription_wrapper(
            batch_request_body: (BatchTranscriptionRequest | BatchTranslationRequest),
        ) -> (
            TranscriptionResponse
            | TranscriptionResponseVerbose
            | TranslationResponse
            | TranslationResponseVerbose
            | ErrorResponse
        ):
            try:
                # Download data from URL
                audio_data = await download_bytes_from_url(batch_request_body.file_url)
```

So the data flow is:

1. Attacker supplies JSON line in the batch input file with arbitrary `body.file_url`.
2. `BatchRequestInput` / `BatchTranscriptionRequest` / `BatchTranslationRequest` parse that JSON and store `file_url` verbatim.
3. `make_transcription_wrapper` calls `download_bytes_from_url(batch_request_body.file_url)`.
4. `download_bytes_from_url`’s HTTP/HTTPS branch issues `aiohttp.ClientSession().get(url)` to that attacker-controlled URL with no further validation.

This is a classic SSRF pattern: a server-side component makes arbitrary HTTP requests to a URL string taken from untrusted input.

#### Comparison with safer code

The project already contains a safer URL-handling path for multimodal media in `vllm/multimodal/media/connector.py`, which demonstrates the intent to mitigate SSRF via domain allowlists and URL normalization:

```
# connector.py Lines 169-189
 def load_from_url(
        self,
        url: str,
        media_io: MediaIO[_M],
        *,
        fetch_timeout: int | None = None,
    ) -> _M:  # type: ignore[type-var]
        url_spec = parse_url(url)

        if url_spec.scheme and url_spec.scheme.startswith("http"):
            self._assert_url_in_allowed_media_domains(url_spec)

            connection = self.connection
            data = connection.get_bytes(
                url_spec.url,
                timeout=fetch_timeout,
                allow_redirects=envs.VLLM_MEDIA_URL_ALLOW_REDIRECTS,
            )

            return media_io.load_bytes(data)
```

and:

```
# connector.py Lines 158-167
  def _assert_url_in_allowed_media_domains(self, url_spec: Url) -> None:
        if (
            self.allowed_media_domains
            and url_spec.hostname not in self.allowed_media_domains
        ):
            raise ValueError(
                f"The URL must be from one of the allowed domains: "
                f"{self.allowed_media_domains}. Input URL domain: "
                f"{url_spec.hostname}"
            )
```

`download_bytes_from_url` does not reuse this allowlist or any equivalent validation, even though it also fetches user-provided URLs.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-pf3h-qjgv-vcpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34753
- https://github.com/vllm-project/vllm/pull/38482
- https://github.com/vllm-project/vllm/commit/57861ae48d3493fa48b4d7d830b7ec9f995783e7
- https://github.com/advisories/GHSA-pf3h-qjgv-vcpr
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3410.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
