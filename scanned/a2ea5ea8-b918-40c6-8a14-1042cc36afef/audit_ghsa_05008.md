# [H] praisonaiagents: SSRF guard validates literal IPs only and never resolves DNS

## Summary
Severity: High
Advisory: GHSA-vxgj-xg5c-p4h7
CVE: CVE-2026-57126
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-vxgj-xg5c-p4h7
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.59

## Details
# praisonaiagents: SSRF guard validates literal IPs only and never resolves DNS

**Researcher:** Kai Aizen — SnailSploit (@SnailSploit), Adversarial & Offensive Security Research
**Target:** https://github.com/MervinPraison/PraisonAI
**Weakness:** CWE-918 Server-Side Request Forgery (SSRF).

---

## Summary

The SSRF guard shared by PraisonAI's web tools (`SpiderTools._validate_url` → `_host_is_blocked` in `praisonaiagents/tools/spider_tools.py`) inspects only **literal IP-address encodings** of the URL host. It never resolves DNS names. Any hostname whose A/AAAA record points at an internal, loopback, link-local, or cloud-metadata address passes validation and the request is issued to that target. A static internal A record is sufficient — no DNS-rebinding race is required.

The guard's own docstring claims it returns `True` "when hostname **resolves to** loopback/private/internal targets," but no resolution is performed. The fix for CVE-2026-47390 added more *encodings of literal IPs* (decimal integer, `0x` hex, `inet_aton`); it did not address the *class* "host is a name that resolves to a forbidden address."

The same guard is reached through two tool surfaces:
- `scrape_page` / `crawl` / `extract_links` / `extract_text` (spider tools)
- the `@url` mention fetch in `praisonaiagents/tools/mentions.py` (which calls the identical `SpiderTools._validate_url` then `urllib.request.urlopen`)

The correct pattern already exists in the same package: `file_tools.py` resolves the host with `socket.getaddrinfo` and checks each resolved address before fetching. `spider_tools` / `mentions` do not.

## Affected packages

- `pip/praisonaiagents` <= 1.6.39
- `pip/PraisonAI` <= 4.6.39

## Root cause

`praisonaiagents/tools/spider_tools.py`, `_host_is_blocked` (def at line 26):

```python
def _host_is_blocked(hostname: str) -> bool:
    """Return True when hostname resolves to loopback/private/internal targets."""
    ...
    if host.isdigit():                                  # decimal-int IPv4 literal
        return _ip_blocked(ipaddress.ip_address(int(host)))
    if host.startswith("0x"):                           # hex IPv4 literal
        return _ip_blocked(ipaddress.ip_address(int(host, 16)))
    try:
        return _ip_blocked(ipaddress.ip_address(host))  # dotted v4 / v6 literal
    except ValueError:
        pass
    try:
        return _ip_blocked(ipaddress.ip_address(socket.inet_aton(host)))  # octal/short v4
    except OSError:
        pass
    return False                                        # <-- any DNS name lands here
```

Every branch operates on the **literal string**. For a DNS name (`attacker.example`): it is not in the literal block sets, not a `.local`/`.internal` suffix, `int(host)` is not applicable, `ipaddress.ip_address(name)` raises `ValueError` (swallowed), `inet_aton(name)` raises `OSError` (swallowed), and the function returns `False` — "not blocked." `socket.getaddrinfo` / `gethostbyname` are never called anywhere in this path.

`_validate_url` (def line 74) ends with:

```python
            if _host_is_blocked(parsed.hostname):
                return False
            return True
```

so a name verdict of "not blocked" yields `_validate_url(...) == True`, and the caller (`scrape_page`, or `mentions._fetch_url` at lines 273–284) proceeds to fetch the original URL via `requests` / `urllib.request.urlopen`.

The literal-IP coverage is otherwise good — Python's `ipaddress.is_reserved` / `is_private` happen to flag NAT64 (`64:ff9b::/96`), 6to4 (`2002::/16`), IPv4-mapped (`::ffff:`), and IPv4-compatible (`::/96`) forms. The single residual literal gap is deprecated site-local `fec0::/10` (`is_private` and `is_reserved` both `False`), which is low-impact on modern stacks. The DNS-name class is the material issue.

### The promise that was broken

The block set explicitly contains `"169.254.169.254"` and `"metadata.google.internal"` (line 33) — documented intent to stop cloud-metadata theft. A name-based request defeats exactly that intent: register `metadata-thief.example` with an A record of `169.254.169.254`, and the literal block is never consulted because resolution never happens.

## Proof of concept

```python
import socket
from praisonaiagents.tools.spider_tools import _host_is_blocked, SpiderTools

# Literal forms the CVE-2026-47390 fix added — correctly blocked:
for h in ["127.0.0.1", "2130706433", "0x7f000001", "169.254.169.254", "::1"]:
    assert _host_is_blocked(h) is True, h

# DNS names that resolve to internal targets — NOT blocked (the class the fix missed):
for h in ["attacker-controlled.example", "metadata-thief.com", "rebind.attacker.net"]:
    assert _host_is_blocked(h) is False, h     # A record may be 127.0.0.1 / 169.254.169.254

st = SpiderTools
assert st._validate_url("http://127.0.0.1/") is False           # literal blocked
assert st._validate_url("http://metadata-thief.com/") is True   # name passes -> request fires

# The guard never even attempts resolution:
import praisonaiagents.tools.spider_tools as S
S.socket.getaddrinfo = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("RESOLVER CALLED"))
assert _host_is_blocked("attacker.example") is False            # no RuntimeError -> never resolved

print("[+] CONFIRMED: SSRF guard ignores DNS resolution; name->internal bypasses validation")
```

End-to-end against a deployed agent: point any controlled domain's A record at `169.254.169.254` (or `127.0.0.1`, or an RFC1918 service), then drive an agent that has `scrape_page`/`crawl` enabled, or include the URL as an `@url` mention. The fetch reaches the internal/metadata target and its response is returned into model context.

## Remediation

Resolve the host and apply the existing `_ip_blocked` check to **every** resolved address before fetching — the pattern already implemented in `praisonaiagents/tools/file_tools.py` (lines 339–344):

```python
resolved = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
for family, _, _, _, sockaddr in resolved:
    if _ip_blocked(ipaddress.ip_address(sockaddr[0])):
        return True   # blocked
```

To also close DNS rebinding (resolve-then-connect TOCTOU), pin the connection to the validated address rather than re-resolving at fetch time. Apply the same fix to both `_validate_url` and `mentions._fetch_url`. Additionally add `fec0::/10` to the IPv6 rejection set for completeness.

## Steps to reproduce

1. Clone the target: `git clone --depth 1 https://github.com/MervinPraison/PraisonAI`
2. Run the proof of concept shown above against the cloned source.
3. Observe the result shown under *Verified result* below.

## Verified result

This PoC was executed against the live upstream code; captured output:

```
== Literal internal/loopback encodings — correctly BLOCKED ==
   127.0.0.1            blocked=True
   2130706433           blocked=True
   0x7f000001           blocked=True
   169.254.169.254      blocked=True
   ::1                  blocked=True
   localhost            blocked=True
   10.0.0.5             blocked=True

== DNS names whose A-record could point internal — NOT blocked (the gap) ==
   attacker-controlled.example  blocked=False
   metadata-thief.com           blocked=False
   rebind.attacker.net          blocked=False

== Prove resolution is NEVER attempted (monkeypatch getaddrinfo to explode) ==
   _host_is_blocked('metadata-thief.com') = False  (no RuntimeError -> DNS never resolved)

== _validate_url verdict (replicating the method's host check on the real func) ==
   http://127.0.0.1/        -> validate=False  (blocked)
   http://metadata-thief.com/ -> validate=True  (PASSES -> request fires)

[+] CONFIRMED: name->internal bypasses the SSRF guard; getaddrinfo/gethostbyname never called.
```

## Credit

Kai Aizen — SnailSploit (@SnailSploit). Adversarial & Offensive Security Research.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-vxgj-xg5c-p4h7
- https://github.com/MervinPraison/PraisonAI
