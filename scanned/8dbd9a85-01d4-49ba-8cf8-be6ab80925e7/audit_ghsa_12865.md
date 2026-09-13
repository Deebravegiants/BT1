# [H] act vulnerable to arbitrary file upload in artifact server

## Summary
Severity: High
Advisory: GHSA-pc99-qmg4-rcff
CVE: CVE-2023-22726
CWE: CWE-22, CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-pc99-qmg4-rcff
Type: github-advisory

## Affected
- Go: `github.com/nektos/act` — affected >=0 <0.2.40

## Details
### Impact
The artifact server that stores artifacts from Github Action runs does not sanitize path inputs. This allows an attacker to download and overwrite arbitrary files on the host from a Github Action. This issue may lead to privilege escalation.


#### Issue 1: Arbitrary file upload in artifact server (GHSL-2023-004)
The [/upload endpoint](https://github.com/nektos/act/blob/v0.2.35/pkg/artifacts/server.go#LL103C2-L103C2) is vulnerable to path traversal as filepath is user controlled, and ultimately flows into os.Mkdir and os.Open.

```
router.PUT("/upload/:runId", func(w http.ResponseWriter, req *http.Request, params httprouter.Params) {
		itemPath := req.URL.Query().Get("itemPath")
		runID := params.ByName("runId")

		if req.Header.Get("Content-Encoding") == "gzip" {
			itemPath += gzipExtension
		}

		filePath := fmt.Sprintf("%s/%s", runID, itemPath)
```

#### Issue 2: Arbitrary file download in artifact server (GHSL-2023-004)
The [/artifact endpoint](https://github.com/nektos/act/blob/v0.2.35/pkg/artifacts/server.go#L245) is vulnerable to path traversal as the path is variable is user controlled, and the specified file is ultimately returned by the server.

```
router.GET("/artifact/*path", func(w http.ResponseWriter, req *http.Request, params httprouter.Params) {
		path := params.ByName("path")[1:]

		file, err := fsys.Open(path)
```

#### Proof of Concept
Below I have written a Github Action that will upload secret.txt into the folder above the specified artifact directory. The first call to curl will create the directory named 1 if it does not already exist, and the second call to curl will upload the secret.txt file to the directory above the specified artifact directory.

When testing this POC, the `--artifact-server-path` parameter must be passed to act in order to enable the artifact server.
Replace yourIPandPort with the IP and port of the server. An attacker can enumerate /proc/net/tcp in order to find the artifact server IP and port, but this is out of the scope of this report. Please let me know if you would like a copy of this script.

```
name: CI
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - run: echo "Here are some secrets" > secret.txt
    - run: curl http://<yourIPandPort>/upload/1?itemPath=secret.txt --upload-file secret.txt
    - run: curl http://<yourIPandPort>/upload/1?itemPath=../../secret.txt --upload-file secret.txt
```

### Remediation
1. During implementation of [Open and OpenAtEnd for FS](https://github.com/nektos/act/blob/master/pkg/artifacts/server.go#L65), please ensure to use ValidPath() to check against path traversal. See more here: https://pkg.go.dev/io/fs#FS
2. Clean the user-provided paths manually

### Patches
Version 0.2.40 contains a patch.

### Workarounds
Avoid use of artifact server with `--artifact-server-path`

## References
- https://github.com/nektos/act/security/advisories/GHSA-pc99-qmg4-rcff
- https://nvd.nist.gov/vuln/detail/CVE-2023-22726
- https://github.com/nektos/act/issues/1553
- https://github.com/nektos/act/commit/63ae215071f94569d910964bdee866d91d6e3a10
- https://github.com/nektos/act
- https://github.com/nektos/act/blob/master/pkg/artifacts/server.go#L65
- https://github.com/nektos/act/blob/v0.2.35/pkg/artifacts/server.go#L245
- https://github.com/nektos/act/blob/v0.2.35/pkg/artifacts/server.go#LL103C2-L103C2
- https://github.com/nektos/act/releases/tag/v0.2.40
- https://securitylab.github.com/advisories/GHSL-2023-004_act
