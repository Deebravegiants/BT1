# [H] Python-Multipart has Arbitrary File Write via Non-Default Configuration

## Summary
Severity: High
Advisory: GHSA-wp53-j4wj-2cfg
CVE: CVE-2026-24486
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-wp53-j4wj-2cfg
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.22

## Details
### Summary

A Path Traversal vulnerability exists when using non-default configuration options `UPLOAD_DIR` and `UPLOAD_KEEP_FILENAME=True`. An attacker can write uploaded files to arbitrary locations on the filesystem by crafting a malicious filename.

### Details

When `UPLOAD_DIR` is set and `UPLOAD_KEEP_FILENAME` is `True`, the library constructs the file path using `os.path.join(file_dir, fname)`. Due to the behavior of `os.path.join()`, if the filename begins with a `/`, all preceding path components are discarded:

```py
os.path.join("/upload/dir", "/etc/malicious") == "/etc/malicious"
```
                        
This allows an attacker to bypass the intended upload directory and write files to arbitrary paths.                                         
                                                                                                                                              
#### Affected Configuration                                                                                                                      
                                                                                                                                              
Projects are only affected if all of the following are true:                                                                                     
- `UPLOAD_DIR` is set
- `UPLOAD_KEEP_FILENAME` is set to True
- The uploaded file exceeds `MAX_MEMORY_FILE_SIZE` (triggering a flush to disk)

The default configuration is not vulnerable.                                                                                                
                                                                                                                                              
#### Impact                                                                                                                                   
                                                                                                                                              
Arbitrary file write to attacker-controlled paths on the filesystem.                                                                        
                                                                                                                                              
#### Mitigation                                                                                                                                  
                                                                                                                                              
Upgrade to version 0.0.22, or avoid using `UPLOAD_KEEP_FILENAME=True` in project configurations.

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-wp53-j4wj-2cfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-24486
- https://github.com/Kludex/python-multipart/commit/9433f4bbc9652bdde82bbe380984e32f8cfc89c4
- https://github.com/Kludex/python-multipart
- https://github.com/Kludex/python-multipart/releases/tag/0.0.22
