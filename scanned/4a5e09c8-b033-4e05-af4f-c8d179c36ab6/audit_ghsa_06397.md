# [C] NLTK: JVM argument injection bypass via per-call options in the NLTK Stanford wrappers (incomplete fix of CVE-2026-12841)

## Summary
Severity: Critical
Advisory: GHSA-m4rf-3fr8-xwx3
CVE: CVE-2026-79675
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-m4rf-3fr8-xwx3
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.3

## Details
## Vulnerability

The fix for CVE-2026-12841 (CWE-88, JVM argument injection) added `_validate_java_options()` to block dangerous JVM flags such as `-agentlib`, `-agentpath`, `-javaagent`, `-Xrunjdwp`, and `@argfile` references. However, the validation is only applied when setting global options via `config_java()`. The `java()` function's per-call `options` parameter -- added by PR #3683 (CVE-2026-12615 fix) -- passes options directly to `subprocess.Popen` without calling `_validate_java_options()`.

All four Stanford Java wrapper classes accept user-supplied `java_options` and route them through the unvalidated per-call path, bypassing the CVE-2026-12841 fix entirely.

## Root Cause

In `nltk/internals.py`, the `java()` function (line 128) accepts an `options` keyword argument. When `options` is not None, it is converted to a list and prepended to the JVM command (lines 211-217) without any validation:

```python
# nltk/internals.py, lines 211-217 (HEAD)
if options is None:
    java_options = _java_options       # validated by config_java()
else:
    if isinstance(options, str):
        options = options.split()
    java_options = list(options)       # NO validation
cmd = [_java_bin] + java_options + cmd
```

Compare with `config_java()` (line 92) which does validate:

```python
# nltk/internals.py, lines 122-123
_validate_java_options(options)
_java_options[:] = options
```

The four affected wrapper classes store user-supplied `java_options` without validation and pass them through the unvalidated per-call path:

1. `GenericStanfordParser` (`nltk/parse/stanford.py`): constructor parameter at line 39, stored at line 78, passed at lines 247 and 256
2. `StanfordTagger` (`nltk/tag/stanford.py`): constructor parameter at line 51, stored at line 79, passed at line 118
3. `StanfordTokenizer` (`nltk/tokenize/stanford.py`): constructor parameter at line 43, stored at line 66, passed at line 109
4. `StanfordSegmenter` (`nltk/tokenize/stanford_segmenter.py`): constructor parameter at line 68, stored at line 117, passed at line 337

## Proof of Concept

```python
from nltk.internals import config_java, java, _validate_java_options

# 1. The global config_java() path correctly blocks dangerous flags:
try:
    config_java(options=["-agentpath:/tmp/evil.so"])
except ValueError as e:
    print(f"config_java blocked: {e}")   # blocked as expected

# 2. The per-call options path does NOT block them:
# (Would execute if Java were installed)
# java(["SomeClass"], classpath=".", options=["-agentpath:/tmp/evil.so"])
# This passes "-agentpath:/tmp/evil.so" directly to subprocess.Popen

# 3. Stanford wrapper classes pass through without validation:
# from nltk.parse.stanford import StanfordParser
# parser = StanfordParser(java_options="-agentpath:/tmp/evil.so")
# parser.parse(...)  # dangerous flag reaches JVM

# Verify the gap directly:
dangerous_opts = ["-agentpath:/tmp/evil.so"]
try:
    _validate_java_options(dangerous_opts)
    print("Would have been caught")
except ValueError:
    print("Correctly rejected by _validate_java_options()")

# But java() itself never calls _validate_java_options():
import inspect
source = inspect.getsource(java)
assert "_validate_java_options" not in source, "java() does not validate options"
print("Confirmed: java() does not call _validate_java_options()")
```

## Impact

An attacker who controls the `java_options` parameter to any NLTK Stanford wrapper class can inject arbitrary JVM flags, including:

- `-agentpath:/path/to/malicious.so` -- loads a native agent, achieving arbitrary code execution
- `-javaagent:/path/to/malicious.jar` -- loads a Java agent for bytecode manipulation
- `-agentlib:jdwp=transport=dt_socket,server=y,address=*:5005` -- enables remote debugging, allowing remote code execution
- `@/path/to/argfile` -- expands an argument file, which can smuggle any of the above

This is exploitable in scenarios where NLTK is deployed as a service and `java_options` is derived from user input, configuration files, or environment variables. The PR #3647 commit message explicitly states the fix was intended to cover "StanfordSegmenter, and GenericStanfordParser" but the implementation only validates in `config_java()`.

## Suggested Fix

Add `_validate_java_options()` to the `java()` function's per-call options handling:

```python
# nltk/internals.py, in the java() function
if options is None:
    java_options = _java_options
else:
    if isinstance(options, str):
        options = options.split()
    java_options = list(options)
    _validate_java_options(java_options)   # ADD THIS LINE
cmd = [_java_bin] + java_options + cmd
```

This single-line addition closes the bypass for all four Stanford wrapper classes and any future callers of `java(options=...)`.

### AI tooling

AI assistance was used for the code audit and for drafting this report. The finding were manually verified against the project's source at the location cited above before reporting it, and the severity and impact assessment are the reporters.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-m4rf-3fr8-xwx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-79675
- https://github.com/nltk/nltk/commit/8fa9650b6009aacfdebbc33d2a08d32c0858ea6c
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.3
- https://www.vulncheck.com/advisories/nltk-before-jvm-argument-injection-via-per-call-options
