# [M] picklescan vulnerable to arbitrary file create using logging.FileHandler

## Summary
Severity: Medium
Advisory: GHSA-m7j5-r2p5-c39r
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-m7j5-r2p5-c39r
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <1.0.1

## Details
### Summary
Unsafe pickle deserialization allows unauthenticated attackers to perform Arbitrary File Creation. By chaining the logging.FileHandler class, an attacker can bypass RCE-focused blocklists to create empty files on the server. The vulnerability allows creating zero-byte files in arbitrary locations but does not permit overwriting or modifying existing files.

### Details
The application deserializes untrusted pickle data. While RCE keywords may be blocked, the exploit abuses standard library features:

logging.FileHandler: The exploit instantiates this class using its default behavior (append mode).

Behavior on Existing Files: If the target file already exists, the handler opens it without modifying its content, resulting in no impact to existing data.

Behavior on Non-Existent Files: If the target file does not exist, the handler creates a new zero-byte file with the specified name.

### PoC
```python
import pickle

class WriteFile:
    def __reduce__(self):
        from logging import FileHandler
        return (FileHandler, ('evil.log',))
    
with open("bypass_write.pkl", "wb") as f:
    pickle.dump(WriteFile(), f)

handler = pickle.loads(pickle.dumps(WriteFile()))
```
<img width="1201" height="140" alt="313e1cfacbe700e27b6875e49808c52a" src="https://github.com/user-attachments/assets/8873bb54-0f98-41aa-8e7c-a38a245ca428" />


### Impact
This primitive can be used for Filesystem Pollution or Logic Disruption. For example, an attacker could create specific "lock files" (e.g., maintenance.lock, .lock) that the application checks for, potentially triggering a Denial of Service (DoS) or preventing the application from starting.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-m7j5-r2p5-c39r
- https://github.com/mmaitre314/picklescan/pull/60
- https://github.com/mmaitre314/picklescan/commit/4d9bc9cd34bca8672dad3481cd4556d5ba747156
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v1.0.1
- https://github.com/pypa/advisory-database/tree/main/vulns/picklescan/PYSEC-2026-225.yaml
- https://www.vulncheck.com/advisories/picklescan-arbitrary-file-creation-via-logging-filehandler-deserialization
