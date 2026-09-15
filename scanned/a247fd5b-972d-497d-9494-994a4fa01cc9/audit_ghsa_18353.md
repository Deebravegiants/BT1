# [C] Picklescan is Vulnerable to Unsafe Globals Check Bypass through Subclass Imports

## Summary
Severity: Critical
Advisory: GHSA-f7qq-56ww-84cr
CVE: CVE-2025-10157
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-f7qq-56ww-84cr
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.31

## Details
### Summary
The vulnerability allows malicious actors to bypass PickleScan's unsafe globals check, leading to potential arbitrary code execution. The issue stems from PickleScan's strict check for full module names against its list of unsafe globals. By using subclasses of dangerous imports instead of the exact module names, attackers can circumvent the check and inject malicious payloads.

### PoC
1. Download a model that uses the `asyncio` package: 

```wget https://huggingface.co/iluem/linux_pkl/resolve/main/asyncio_asyncio_unix_events___UnixSubprocessTransport__start.pkl```

2. Check with PickleScan: `picklescan -p asyncio_asyncio_unix_events___UnixSubprocessTransport__start.pkl -g`

**Expected Result:**

PickleScan should identify all `asyncio` import as dangerous and flag the pickle file as malicious as `asyncio` is in `_unsafe_globals` dictionary.

**Actual Result:**
![Screenshot 2025-06-29 at 14 13 38](https://github.com/user-attachments/assets/39467f50-5cdb-4c25-bb37-35c03dc4a626)

PickleScan marked the import as Suspicious, failing to identify it as a dangerous import.

### Impact
**Severity**: High
**Affected Users**: Any organization, like HuggingFace, or individual using PickleScan to analyze PyTorch models or other files distributed as ZIP archives for malicious pickle content.
**Impact Details**: Attackers can craft malicious PyTorch models containing embedded pickle payloads, package them into ZIP archives, and bypass the PickleScan check by using subclasses of dangerous imports. This could lead to arbitrary code execution on the user's system when these malicious files are processed or loaded.

**Recommendations:**

**Replace:**
https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L309C9-L309C54


  `      unsafe_filter = _unsafe_globals.get(g.module)`

by:
```
      matched_key = None
        if imported_global.module:
            for key_in_globals in unsafe_globals.keys():
                # Check if imported_global.module starts with the key_in_globals AND
                # (it's the first match OR this key is more specific than the previous match)
                # AND imported_global.module is exactly the key or imported_global.module is key + '.' + something
                if imported_global.module.startswith(key_in_globals):
                    if (imported_global.module == key_in_globals or # Exact match
                            (len(imported_global.module) > len(key_in_globals) and imported_global.module[len(key_in_globals)] == '.')): # Submodule match
                        if matched_key is None or len(key_in_globals) > len(matched_key):
                            matched_key = key_in_globals

        if matched_key:
            unsafe_filter = unsafe_globals[matched_key]
```

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-f7qq-56ww-84cr
- https://nvd.nist.gov/vuln/detail/CVE-2025-10157
- https://github.com/mmaitre314/picklescan/pull/50
- https://github.com/mmaitre314/picklescan/commit/28a7b4ef753466572bda3313737116eeb9b4e5c5
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L309
- https://github.com/pypa/advisory-database/tree/main/vulns/picklescan/PYSEC-2025-153.yaml
- https://huggingface.co/iluem/linux_pkl/resolve/main/asyncio_asyncio_unix_events___UnixSubprocessTransport__start.pkl
