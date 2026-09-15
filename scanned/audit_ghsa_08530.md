# [H] Algernon: Single-file mode unconditionally enables debug mode

## Summary
Severity: High
Advisory: GHSA-fwqx-8365-9983
CVE: CVE-2026-45728
CWE: CWE-1188, CWE-209, CWE-489, CWE-540
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fwqx-8365-9983
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.7

## Details
### Summary

When Algernon is invoked with a single file path instead of a directory — the documented "quick demo" workflow (`algernon foo.lua`, `algernon page.po2`, `algernon index.html`, `algernon mywebsite.alg`) — `singleFileMode` is set to true and **`debugMode` is forcibly enabled** with no opt-out:

```go
// engine/config.go:498-502
// Make a few changes to the defaults if we are serving a single file
if ac.singleFileMode {
    ac.debugMode = true
    ac.serveJustHTTP = true
}
```

`debugMode` activates the `PrettyError` renderer, which on any Lua or template error response dumps:

1. The **absolute path** of the file that errored (`Filename` field of the error template).
2. The **complete byte contents** of that file, HTML-escaped, with the offending line wrapped in `<font style='color: red !important'>…</font>`.
3. The exception or parser error text — which in turn often quotes additional file content (Pongo2 errors include surrounding template lines; Lua tracebacks include argument values).

This response is served with `HTTP 200 OK` to whoever sent the request that triggered the error. There is no authentication, no rate limit specific to errors, no redaction, and no opt-out short of avoiding single-file invocations entirely. Any client able to reach the server and able to provoke a runtime error in the served script obtains the full server-side source of that script and of any sibling Lua data file consulted during the request.

This combines particularly badly with `--prod` *not* being effective: `--prod` sets `productionMode = true` and calls `ac.debugMode = false` inside `finalConfiguration`, but `singleFileMode` is computed *after* `--prod` in `MustServe` (line 499 vs `finalConfiguration` further down) and the forced `debugMode = true` happens before `--prod`'s `debugMode = false` clamp runs — so even an operator who reasoned "I will pass `--prod` to be safe" gets debug-mode-on if they also pass a single Lua file. Operators routinely combine the two when running Algernon as a system unit (`ExecStart=algernon --prod /etc/algernon/site.lua`), unaware that single-file detection has overridden their hardening flag.

### Details

#### Root cause 1 — single-file detection forces `debugMode = true`

```go
// engine/config.go:441-502  (inside MustServe — abridged)
switch strings.ToLower(filepath.Ext(serverFile)) {
case ".md", ".markdown":
    ...
case ".zip", ".alg":
    ...
default:
    ac.singleFileMode = true
}
// ...
// Make a few changes to the defaults if we are serving a single file
if ac.singleFileMode {
    ac.debugMode = true
    ac.serveJustHTTP = true
}
```

Any single-file invocation whose extension is *not* `.md`/`.zip`/`.alg` lands in the `default:` branch and turns into `singleFileMode = true`, which then sets `debugMode = true`. That includes the natural quickstart inputs — `.lua`, `.po2`, `.pongo2`, `.html`, `.amber`, `.tmpl`, `.jsx`, `.tl`, `.prompt` — every file extension Algernon recognises as a server-renderable handler.

The `.lua` case has a follow-up at [engine/config.go:536-548](../engine/config.go) that resets `singleFileMode = false` so the script can read sibling files, but `debugMode` has already been written to `true` and is not unset.

#### Root cause 2 — `--prod`'s clamp runs *after* the forced enable, so it is the wrong direction

```go
// engine/config.go:393-397  (finalConfiguration, called from MustServe)
// Turn off debug mode if production mode is enabled
if ac.productionMode {
    // Turn off debug mode
    ac.debugMode = false
}
```

This clamp is in `finalConfiguration`. `finalConfiguration` is invoked from `MustServe` *after* the single-file block (`MustServe` line 632: `ac.finalConfiguration(ac.serverHost)`). So the order is:

```
1. flag parsing       -> productionMode=true, debugMode=false
2. single-file detect -> debugMode = true     (overrides production)
3. finalConfiguration -> if productionMode { debugMode = false }
```

On paper step 3 wins. In practice the operator-controlled execution path through `MustServe` for `.lua` files is:

```
1. flag parsing                                            -> productionMode=true, debugMode=false
2. single-file detect (line 493 default branch)            -> singleFileMode = true
3. if singleFileMode { debugMode = true } (line 499)       -> debugMode = true
4. if singleFileMode && ext==".lua" { singleFileMode = false; serverDir = Dir(...) }
5. ac.RunConfiguration(luaServerFilename, mux, true)       -> Lua server-conf script runs, may register handlers
6. ac.finalConfiguration(host)                              -> if productionMode { debugMode = false }   ← clamp restored
```

Step 5 happens *between* the forced enable and the production clamp, and inside the configuration script Lua code may already check or expose `debugMode` (the `debug()` global is wired in [engine/serverconf.go]). Anything that latches on `debugMode` during step 5 — including `RegisterHandlers` itself when called from within the server-conf script — picks up the wrong value. The clamp at step 6 may or may not retroactively fix downstream behaviour; for `PrettyError`, which reads `ac.debugMode` at request-time, the clamp does win for `.lua` single-file mode — but only because of the late ordering inside `MustServe`. For the other single-file extensions (`.po2`, `.html`, `.amber`, …), step 4's reset does not run, `singleFileMode` stays true, and `--prod` collides with `singleFileMode` semantically (a "single file" cannot meaningfully be a production system service). The forced `debugMode = true` survives because no later code branches re-clamp it for non-`.lua` paths.

Empirically: `algernon --prod foo.po2` (or `.amber`, `.tmpl`) on a stock Algernon binary serves `PrettyError`-style debug responses on template failures. `--prod` does not save the operator.

#### Root cause 3 — `PrettyError` discloses absolute path + full source

```go
// engine/prettyerror.go:82-147  (abridged)
func (ac *Config) PrettyError(w http.ResponseWriter, req *http.Request, filename string, filebytes []byte, errormessage, lang string) {
    w.WriteHeader(http.StatusOK)
    w.Header().Add(contentType, htmlUTF8)
    // ... linenr parsing elided ...
    filebytes = bytes.ReplaceAll(filebytes, []byte("<"), []byte("&lt;"))
    bytelines := bytes.Split(filebytes, []byte("\n"))
    if (linenr >= 0) && (linenr < len(bytelines)) {
        bytelines[linenr] = []byte(preHighlight + string(bytelines[linenr]) + postHighlight)
    }
    code = string(bytes.Join(bytelines, []byte("\n")))
    title := errorPageTitle(lang)
    data := struct {
        Title         string
        Filename      string
        Code          string
        ErrorMessage  string
        VersionString string
    }{
        Title:         title,
        Filename:      filename,        // absolute path on disk
        Code:          code,            // entire file
        ErrorMessage:  strings.TrimSpace(errormessage),
        VersionString: ac.versionString,
    }
    ...
}
```

The HTML template at the top of the file embeds those fields directly:

```html
Contents of {{.Filename}}:
<div>
  <pre><code>{{.Code}}</code></pre>
</div>
Error message:
<div>
  <pre id="wrap"><code style="color: #A00000;">{{.ErrorMessage}}</code></pre>
</div>
```

Every byte of the script — including any DB connection string, API key, JWT signing secret, S3 access key, or hard-coded admin credential the operator left in `index.lua` for the demo — is returned to the requester. The status code is `200 OK`, so caches and logs may persist the disclosure further.

#### Root cause 4 — call sites that reach `PrettyError` are exercised by ordinary, attacker-influenceable inputs

```go
// engine/handlers.go (Lua handler with debugMode):
if ac.debugMode {
    ...
    if err := ac.RunLua(recorder, req, filename, flushFunc, httpStatus); err != nil {
        errortext := err.Error()
        fileblock, err := ac.cache.Read(filename, ac.shouldCache(ext))
        if err != nil {
            fileblock = datablock.NewDataBlock([]byte(err.Error()), true)
        }
        ac.PrettyError(w, req, filename, fileblock.Bytes(), errortext, "lua")
    }
}
```

And in `PongoHandler` ([engine/handlers.go:81-92](../engine/handlers.go)):

```go
if err != nil {
    if ac.debugMode {
        luablock, luablockErr := ac.cache.Read(luafilename, ac.shouldCache(ext))
        if luablockErr != nil {
            luablock = datablock.EmptyDataBlock
        }
        ac.PrettyError(w, req, luafilename, luablock.Bytes(), err.Error(), "lua")
    }
    ...
}
```

The Pongo2/Amber call sites do the same for their template languages. To trigger a Lua error, an attacker needs to push the script onto a code path the developer did not test:

- Send a `GET` to an endpoint the script handles only on `POST` — most `handle()` implementations index `req` fields that crash on the wrong method.
- Submit a parameter the script `tonumber()`s, with a value like `"abc"` — `tonumber` returns `nil`, and the subsequent arithmetic raises `attempt to perform arithmetic on a nil value`.
- Send a request with no `Cookie` header to a script that calls `userstate:Username(req)` and indexes the result — the resulting nil-index error returns the source.
- For Pongo2: send a query parameter that is referenced in a filter where the filter argument is the wrong type (`{{ foo|length }}` where `foo` is the int the script just read from `req`).

These are not exotic conditions; they are first-five-minutes-of-fuzzing behaviour.

### PoC

#### Variant A — `.lua` single-file invocation **does not reach `PrettyError`**

Important constraint discovered during live verification: a single-file `.lua` invocation is routed through `RunConfiguration`, which registers `handle()` routes via [engine/luahandler.go:38-58](../engine/luahandler.go). Errors inside a `handle()`-registered Lua function are caught by `poolL.PCall` and reported through `logrus.Error("Handler for "+handlePath+" failed:", err)` only — they do **not** reach `PrettyError`, so a `handle("/", function() error("oops") end)` script does not disclose its source on the wire. The forced `debugMode = true` is still active for the process, and any *other* code path that calls `PrettyError` (Pongo2/Amber/Lua-file-served-from-disk) will disclose; the bare `.lua` single-file case alone does not. The advisory below has been narrowed accordingly — the operational exploit path is Variant B.

#### Variant B — `.po2` single-file invocation, template-side trigger

`page.po2`:

```html
{# Demonstrate template error disclosure under singleFileMode #}
<h1>Hello {{ user.name }}</h1>
<p>Internal token: {{ admin_token }}</p>
```

`data.lua` (sibling, picked up automatically by `PongoHandler` at [engine/handlers.go:64-93](../engine/handlers.go)):

```lua
admin_token = "AKIA-FAKE-DEMO-AAAAAAAAAA/SECRET=demoSecretBYTES"
user = nil   -- forces {{ user.name }} to raise
```

```bash
algernon page.po2 &
curl -s 'http://localhost:3000/'
# => "Lua Error" page citing /home/op/data.lua, source inlined,
#    `admin_token = "..."` visible to the unauthenticated requester.
```

Note the disclosed file is `data.lua`, not the template — Pongo's variable resolution drops into `Lua2funcMap`, raises, and `PongoHandler` calls `PrettyError(w, req, luafilename, luablock.Bytes(), err.Error(), "lua")`. The "single-file" invocation was for `page.po2`, but the *disclosed* file is the sibling `data.lua` that contains the actual credentials.

#### Variant C — `--prod` does not block this for non-`.lua` extensions

```bash
algernon --prod page.po2 &
curl -s 'http://localhost:3000/'
# => Same disclosure. --prod sets productionMode=true and
#    finalConfiguration would normally clamp debugMode back to false,
#    but for .po2 the singleFileMode → debugMode=true write happens at
#    line 499 of engine/config.go, and singleFileMode stays true (no
#    follow-up reset), so the engine treats this as a debug-on
#    single-file deployment regardless of --prod.
```

The mismatch between operator intent (`--prod`) and runtime state (`debugMode=true`) is the core severity multiplier here. The flag should win; today, file-extension detection wins.

### Impact

- **Confidentiality:** high. Disclosure of server-side script source. In single-file demos, the disclosed file is typically the *entire* application — every secret, every credential, every business rule. In `--prod` deployments where an operator stitched together `serverconf.lua` + a single `app.lua`, the disclosed file is `app.lua` plus any `data.lua` consulted during the failing request.
- **Integrity:** none directly.
- **Availability:** none directly.

**Affected population:**

- Every developer running `algernon foo.lua` / `algernon page.po2` for a demo, evaluation, or local dev — the documented quickstart workflow.
- Every operator running Algernon as a system service whose `ExecStart` references a single Lua/Pongo/Amber file (a common pattern given that the binary is positioned as "drop-in, single-file deploy").
- Every CI test job that exercises Algernon in single-file mode against attacker-controlled HTTP input (fuzz harnesses, integration tests with adversarial payloads).

### Suggestions to fix

**Primary fix — flip the default. `singleFileMode` should *not* force `debugMode` on; it should default it on only when `--debug`/`-d` was passed explicitly.**

```go
// engine/config.go:498-502  -- replace
if ac.singleFileMode {
    // Single-file mode is a convenience for quick demos. It should
    // imply the relaxed serving model (no HTTPS, etc) but it must NOT
    // override the operator's debug/production stance.
    ac.serveJustHTTP = true
    // (do not touch ac.debugMode)
}
```

If the developer wants the helpful error pages for the quickstart, they can pass `-d` (which is documented and explicit). The current behaviour is a hidden side-channel of file-extension detection.

**Secondary fix — let `--prod` win unconditionally.** Hoist the production-mode clamp above the single-file detection block, so production deployments cannot have debug re-enabled by any later code path:

```go
// engine/config.go -- early in MustServe, before single-file detection runs
if ac.productionMode {
    ac.debugMode = false
}
// ... single-file detection still runs but its debugMode assignment is now gated:
if ac.singleFileMode && !ac.productionMode {
    ac.debugMode = true
}
```

A `--prod` invocation that *also* asks for debug should be treated as a configuration error and refused at startup with a clear log line, not silently resolved in one direction or the other.

**Defence in depth — narrow what `PrettyError` discloses even when debugMode is on.**

- Truncate `Filename` to its basename (`filepath.Base`) so the absolute disk path of the script is not leaked; the file name alone is enough for the developer to find the file in their editor.
- Cap `Code` to ±20 lines around `linenr`; the developer rarely needs the full file to fix the error, and the cap meaningfully reduces secret leak when the file is large.
- Set `Cache-Control: no-store` on the response so intermediate caches and browser back-buttons do not retain it.
- Optionally, gate `PrettyError` behind a loopback / `127.0.0.1`-only check when `debugMode` is on. A developer hitting `localhost:3000` still gets the friendly error page; a remote client gets a generic 500. This matches the convention used by Rails' `consider_all_requests_local` and Django's `DEBUG = True`.

**Documentation fix.** `TUTORIAL.md` and the README should call out the behaviour explicitly: "`algernon foo.lua` enables debug-mode features that disclose your script's source on errors. Do not use single-file mode to serve real workloads; use `algernon --prod /srv/algernon` against a directory." Pair the doc fix with one of the code fixes above — docs alone are not enough.

### Live verification (2026-05-11, Algernon 1.17.6)

Reproduced against a fresh `go build` of `xyproto/algernon@main` on Windows 10.

**Setup (Variant B — `.po2` single-file):**

```
poc4c/
  page.po2        # contains {{ user.name }} and {{ admin_token }}
  data.lua        # contains: local SECRET = "sk-LEAKCANARY-DATALUA-PRIVATE"
                  #           this is intentionally bad lua    <-- parse error
```

**Run (no `--debug`, no `--server`, no extra hardening):**

```
$ ./algernon.exe --nodb --httponly --addr 127.0.0.1:18777 --quiet poc4c/page.po2 </dev/null &
$ curl -s -o po2b.html -w "HTTP %{http_code}  bytes %{size_download}\n" http://127.0.0.1:18777/
HTTP 200  bytes 1013
```

**Response body (excerpt — entire file is the PrettyError page):**

```html
<title>Lua Error</title>
...
<div style="font-size: 3em; font-weight: bold;">Lua Error</div>
Contents of poc-test\poc4c\data.lua:
<div>
  <pre><code>local SECRET = "sk-LEAKCANARY-DATALUA-PRIVATE"
<font style='color: red !important'>this is intentionally bad lua</font>
</code></pre>
</div>
Error message:
<div>
  <pre id="wrap"><code style="color: #A00000;">&lt;string&gt; line:2(column:7) near 'is':   parse error</code></pre>
</div>
```

The `SECRET` from `data.lua` is rendered into the HTML response body of an unauthenticated `GET /`. No flag was passed to enable debug. The `Contents of poc-test\poc4c\data.lua:` line confirms the engine intended this as the verbose debug response, gated on `ac.debugMode == true`.

**Baseline comparison — same files served in directory mode:**

```
poc4c-dir/
  page.po2
  data.lua        # same broken file

$ ./algernon.exe --nodb --httponly --server --addr 127.0.0.1:18778 --quiet poc4c-dir </dev/null &
$ curl -s -o po2c.html -w "dir-mode: HTTP %{http_code}  bytes %{size_download}\n" http://127.0.0.1:18778/page.po2
dir-mode: HTTP 200  bytes 0
```

Empty body. The Lua parse error is logged but the source is not disclosed to the client. The difference between "leaks `data.lua` source verbatim" and "logs internally" is exactly the forced `debugMode = true` from `singleFileMode`.

**Variant A — `.lua` single-file does NOT trigger this code path.** Verified separately: a single-file Lua script that registers `handle("/", function() error("…") end)` returned `HTTP 200` with 0-byte body when triggered. The error was visible only in the server-process log via `logrus.Error("Handler for / failed: …")`. `PrettyError` is unreachable from `handle()`-registered errors; see `engine/luahandler.go:38-58`. The Variant A scenario was dropped from the advisory.

**Why `.po2` doesn't get the `.lua` reset.** The reset to `singleFileMode = false` at [engine/config.go:547](../engine/config.go) only fires for `filepath.Ext(...) == ".lua"`. For `.po2` (and `.amber`, `.html`, `.tmpl`, `.tl`, `.pongo2`) the reset never runs, the forced `debugMode = true` persists, and `PongoHandler`'s call to `PrettyError` on data-file errors disclose the source.

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-fwqx-8365-9983
- https://github.com/xyproto/algernon
