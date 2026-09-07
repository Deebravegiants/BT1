# [H] NLTK: Default ENFORCE=False Disables All pathsec Security Controls

## Summary
Severity: High
Advisory: GHSA-p3m8-78j2-g5p3
CVE: CVE-2026-62388
CWE: CWE-1188
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-p3m8-78j2-g5p3
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
NLTK's pathsec.py security module defaults to ENFORCE=False (line 24), which means all 8 security validation functions only emit RuntimeWarning instead of raising exceptions when violations are detected.

The pathsec module was introduced as the fix for CVE-2024-39705 (arbitrary code execution via pickle) and CVE-2026-0846 (path traversal). However, with ENFORCE=False as the default:

1. pathsec.open('/etc/passwd') succeeds (reads the file, emits warning)
2. pathsec.validate_network_url('http://169.254.169.254/...') succeeds (warning only)
3. pickle.loads() via nltk.data.load() proceeds despite unsafe source (warning only)

Every security gate follows the same pattern:
```python
ENFORCE = os.environ.get('NLTK_PATHSEC_ENFORCE', '').lower() in ('1', 'true', 'yes')

def validate_something(path):
    if is_violation(path):
        if ENFORCE:
            raise SecurityError('...')  # Only raised when env var is set
        else:
            warnings.warn('...', RuntimeWarning)  # Default: warning only
    # Execution continues regardless
```

This means the security remediations for CVE-2024-39705 and CVE-2026-0846 are effectively disabled by default. Any user who installed NLTK 3.9.x expecting the security fixes to be active is still vulnerable unless they manually set NLTK_PATHSEC_ENFORCE=1.

PoC:
```python
import nltk.pathsec
import warnings

# Show that ENFORCE is False by default
print(f'ENFORCE = {nltk.pathsec.ENFORCE}')  # False

# Attempt to read /etc/passwd through pathsec -- should be blocked
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    result = nltk.pathsec.open('/etc/passwd', 'r')
    print(f'File opened: {result.name}')  # /etc/passwd
    print(f'Warning emitted: {w[0].message}')  # RuntimeWarning (not an exception)
    # Attack succeeds -- file is readable
```

The correct default is fail-secure: ENFORCE should be True unless explicitly disabled. The current default makes the security module opt-in rather than opt-out, defeating its purpose.

Suggested fix: Change default to ENFORCE=True. Users who need backwards compatibility can set NLTK_PATHSEC_ENFORCE=0 to explicitly disable.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-p3m8-78j2-g5p3
- https://nvd.nist.gov/vuln/detail/CVE-2026-62388
- https://github.com/nltk/nltk/pull/3593
- https://github.com/nltk/nltk/commit/155e40343cff0bf50d233e274a12e04d1428b1d9
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.0
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3722.yaml
- https://www.vulncheck.com/advisories/nltk-before-insecure-default-configuration-pathsec
