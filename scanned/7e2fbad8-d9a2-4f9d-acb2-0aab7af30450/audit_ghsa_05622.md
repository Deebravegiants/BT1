# [H] GuardDog Path Traversal Vulnerability Leads to Arbitrary File Overwrite and RCE

## Summary
Severity: High
Advisory: GHSA-xg9w-vg3g-6m68
CVE: CVE-2026-22871
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-xg9w-vg3g-6m68
Type: github-advisory

## Affected
- PyPI: `guarddog` — affected >=0 <2.7.1

## Details
## Summary

A **path traversal vulnerability** exists in GuardDog's `safe_extract()` function that allows malicious PyPI packages to write arbitrary files outside the intended extraction directory, leading to **Arbitrary File Overwrite** and **Remote Code Execution** on systems running GuardDog.

**CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)

## Details

### Vulnerable Code

**File:** `guarddog/utils/archives.py`

```python
elif zipfile.is_zipfile(source_archive):
    with zipfile.ZipFile(source_archive, "r") as zip:
        for file in zip.namelist():
            # Note: zip.extract cleans up any malicious file name
            # such as directory traversal attempts This is not the
            # case of zipfile.extractall
            zip.extract(file, path=os.path.join(target_directory, file))  # ❌ VULNERABLE
```

### Root Cause

The comment about `zip.extract()` fooled me at first :) then I noticed the `os.path.join()` call. 
The vulnerability stems from **incorrect usage of Python's `zipfile.ZipFile.extract()` API**:

- The `path` parameter should be the **target directory**, not a full file path
- `extract()` automatically appends the member name to the path
- By passing `os.path.join(target_directory, file)`, GuardDog causes the filename to be appended **twice**
- This breaks zipfile's built-in path traversal sanitization

### Attack Vector

1. Attacker creates malicious wheel with path traversal filenames
2. Uploads to PyPI or distributes directly
3. Package scan: `guarddog pypi scan malicious-pkg`
4. GuardDog downloads and extracts the package
5. Malicious files written to arbitrary locations
6. Code execution could be achieved

## Impact

Impact depends on how GuardDog is running and under which environment.

### Critical Scenarios

1. **Immediate Code Execution**
   - Write to `~/.bashrc` → executes on next shell
   - Write to `~/.profile` → executes on login

2. **Persistent Backdoors**
   - Write to `~/.ssh/authorized_keys` → SSH access
   - Write to `/etc/cron.d/malicious` → scheduled execution (if root)
   - Write to systemd user services → persistent execution

and more...

## Credits

**Reported by:** Charbel (dwbruijn)

## References
- https://github.com/DataDog/guarddog/security/advisories/GHSA-xg9w-vg3g-6m68
- https://nvd.nist.gov/vuln/detail/CVE-2026-22871
- https://github.com/DataDog/guarddog/commit/9aa6a725b2c71d537d3c18d1c15621395ebb879c
- https://github.com/DataDog/guarddog
