# [M] Scapy Session Loading Vulnerable to Arbitrary Code Execution via Untrusted Pickle Deserialization

## Summary
Severity: Medium
Advisory: GHSA-cq46-m9x9-j8w2
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-cq46-m9x9-j8w2
Type: github-advisory

## Affected
- PyPI: `scapy` — affected >=0

## Details
### Summary

An unsafe deserialization vulnerability in Scapy <v2.7.0 allows attackers to execute arbitrary code **when a malicious session file is locally loaded via the `-s` option**. This requires convincing a user to manually load a malicious session file.

---

### Details

Scapy’s interactive shell supports session loading using gzip-compressed pickle files:

```bash
./run_scapy -s <session_file.pkl.gz>
```

Internally, this triggers:

```python
# main.py
SESSION = pickle.load(gzip.open(session_name, "rb"))
```

Since no validation or restriction is performed on the deserialized object, **any code embedded via `__reduce__()` will be executed immediately**. This makes it trivial for an attacker to drop a malicious `.pkl.gz` in a shared folder and have it executed by unsuspecting users.

The vulnerability exists in the `load_session` function, which deserializes data using `pickle.load()` on `.pkl.gz` files provided via the `-s` CLI flag or programmatically through `conf.session`.

**Affected lines in source code**:
https://github.com/secdev/scapy/blob/master/scapy/main.py#L569-L572

```python
try:
    s = pickle.load(gzip.open(fname, "rb"))
except IOError:
    try:
        s = pickle.load(open(fname, "rb"))
```

### Impact

This is a classic deserialization vulnerability which leads to Code Execution (CE) when untrusted data is deserialized.

Any user who can trick another user into loading a crafted `.pkl.gz` session file (e.g. via `-s` option) can execute arbitrary Python code.

- **Vulnerability type:** Insecure deserialization (Python `pickle`)
- **CWE**: [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
- **CVSS v4.0 Vector**: `CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **CVSS Score**: 5.4 (Medium)
- **Impact:** Arbitrary Code Execution
- **Attack vector:** Local or supply chain (malicious `.pkl.gz`)
- **Affected users:** Any user who loads session files (even interactively)
- **Affected version:** **Scapy v2.6.1**

---

### Mitigations

- Do not use 'sessions' (the -s option when launching Scapy).
- Use the Scapy 2.7.0+ where the session mechanism has been removed.

## References
- https://github.com/secdev/scapy/security/advisories/GHSA-cq46-m9x9-j8w2
- https://github.com/secdev/scapy/commit/13621d1145b3435e9d03caf20997107a84435c0b
- https://github.com/secdev/scapy
