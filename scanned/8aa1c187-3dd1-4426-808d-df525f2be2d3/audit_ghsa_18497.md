# [M] Assemblyline 4 service client vulnerable to Arbitrary Write through path traversal in Client code 

## Summary
Severity: Medium
Advisory: GHSA-75jv-vfxf-3865
CVE: CVE-2025-55013
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-75jv-vfxf-3865
Type: github-advisory

## Affected
- PyPI: `assemblyline-service-client` — affected >=0 <4.6.0.stable11
- PyPI: `assemblyline-service-client` — affected >=4.6.1.dev0 <4.6.1.dev138

## Details
**Path-Traversal -> Arbitrary File Write in Assemblyline Service Client**

**IMPORTANT**: This vulnerability is valid if you decide to use the assemblyline-service-client outside of the normal practice to using Assemblyline in a production environment. In practice, this code should always be executed within a containerized environment such as [assemblyline-v4-service](https://github.com/CybercentreCanada/assemblyline-v4-service) which ensures filesystem-level permissions of what the running user is allowed to access. Furthermore, there is fewer chances for a MiTM compromise when deployed properly in a Docker or Kubernetes deployment where the platform will assign the correct network policies to secure connections between containers instead of relying on the user to set this up manually.

See https://github.com/CybercentreCanada/assemblyline/issues/382 for further discussion.

---

## 1. Summary  
The Assemblyline 4 **service client** (`task_handler.py`) accepts a SHA-256 value returned by the service **server** and uses it directly as a local file name.  
> No validation / sanitisation is performed.

A **malicious or compromised server** (or any MITM that can speak to client) can return a path-traversal payload such as  
`../../../etc/cron.d/evil`  
and force the client to write the downloaded bytes to an arbitrary location on disk.

---

## 2. Affected Versions  
| Item | Value |
|---|---|
| **Component** | `assemblyline-service-client` |
| **Repository** | [CybercentreCanada/assemblyline-service-client](https://github.com/CybercentreCanada/assemblyline-service-client) |
| **Affected** | **All releases up to master branch.**  |


---

## 3. CVSS 3.1 Vector & Score  
```
CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L
```


---

## 4. Technical Details

| Field | Content |
|---|---|
| **Location** | `assemblyline_service_client/task_handler.py`, inside `download_file()` |
| **Vulnerable Line** | `file_path = os.path.join(self.tasking_dir, sha256)` |
| **Root Cause** | The `sha256` string is taken directly from the service-server JSON response and used as a file name without any validation or sanitisation. |
| **Exploit Flow** | 1. Attacker (service server) returns HTTP 200 for `GET /api/v1/file/../../../etc/cron.d/evil`.<br>2. Client writes the response body to `/etc/cron.d/evil`.<br>3. Achieves arbitrary file write (code execution if file is executable). |

---

## 5. Impact  
- **Integrity** – Overwrite any file writable by the service UID (often root).  
- **Availability** – Corrupt critical files or exhaust disk space.  
- **Code Execution** – Drop cron jobs, systemd units, or overwrite binaries.

---

## 6. Mitigation / Fix

```python
import re

_SHA256_RE = re.compile(r'^[0-9a-fA-F]{64}\Z')

def download_file(self, sha256: str, sid: str) -> Optional[str]:
    if not _SHA256_RE.fullmatch(sha256):
        self.log.error(f"[{sid}] Invalid SHA256: {sha256}")
        self.status = STATUSES.ERROR_FOUND
        return None
    # or your preferred way to check if a string is a shasum.
```
---

## References
- https://github.com/CybercentreCanada/assemblyline/security/advisories/GHSA-75jv-vfxf-3865
- https://nvd.nist.gov/vuln/detail/CVE-2025-55013
- https://github.com/CybercentreCanada/assemblyline-service-client/commit/351414e7e96cc1f5640ae71ae51b939e8ba30900
- https://github.com/CybercentreCanada/assemblyline-service-client
