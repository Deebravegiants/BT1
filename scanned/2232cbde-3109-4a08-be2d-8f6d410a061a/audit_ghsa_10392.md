# [C] Kedro has Arbitrary Code Execution via Malicious Logging Configuration

## Summary
Severity: Critical
Advisory: GHSA-9cqf-439c-j96r
CVE: CVE-2026-35171
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9cqf-439c-j96r
Type: github-advisory

## Affected
- PyPI: `kedro` — affected >=0 <1.3.0

## Details
### Impact

This is a **critical remote code execution (RCE)** vulnerability caused by unsafe use of `logging.config.dictConfig()` with user-controlled input.

Kedro allows the logging configuration file path to be set via the `KEDRO_LOGGING_CONFIG` environment variable and loads it without validation. The logging configuration schema supports the special `()` key, which enables arbitrary callable instantiation. An attacker can exploit this to execute arbitrary system commands during application startup.

---

### Patches

The vulnerability is fixed by introducing validation that rejects the unsafe `()` factory key in logging configurations before passing them to `dictConfig()`.

#### Fixed in
- Kedro 1.3.0

Users should upgrade to this version as soon as possible.

---

### Workarounds

If upgrading is not immediately possible:

- Do not allow untrusted input to control the `KEDRO_LOGGING_CONFIG` environment variable  
- Restrict write access to logging configuration files  
- Avoid using externally supplied or dynamically generated logging configs  
- Manually validate logging YAML to ensure it does not contain the `()` key  

These mitigations reduce risk but do not fully eliminate it.

---

### References

- Python logging configuration documentation: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema  
- CWE-94: Code Injection — https://cwe.mitre.org/data/definitions/94.html

## References
- https://github.com/kedro-org/kedro/security/advisories/GHSA-9cqf-439c-j96r
- https://nvd.nist.gov/vuln/detail/CVE-2026-35171
- https://github.com/kedro-org/kedro
- https://github.com/pypa/advisory-database/tree/main/vulns/kedro/PYSEC-2026-72.yaml
