# [H] NiceGUI: Local file disclosure via Docutils file insertion in ui.restructured_text()

## Summary
Severity: High
Advisory: GHSA-jfrm-rx66-g536
CVE: CVE-2026-45553
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-jfrm-rx66-g536
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.12.0

## Details
### Summary

`ui.restructured_text()` renders reStructuredText server-side with Docutils without disabling file insertion directives.

When a NiceGUI application passes attacker-controlled content to `ui.restructured_text()`, an attacker can use standard Docutils directives (`include`, `csv-table` with `:file:`, `raw` with `:file:`) to read local files readable by the NiceGUI server process.

Applications that only pass trusted static strings to `ui.restructured_text()` are not affected.

### Details

The affected component is the reStructuredText renderer:

- File: `nicegui/elements/restructured_text.py`
- Function: `prepare_content()`

`prepare_content()` renders user-supplied reStructuredText through Docutils:

```python
html = publish_parts(
    remove_indentation(content),
    writer_name='html4',
    settings_overrides={'syntax_highlight': 'short'},
)
```

The Docutils call only sets `syntax_highlight`. It does not disable file insertion or raw directives, so Docutils processes directives that read local files and embed their contents into the generated HTML before it is returned to the browser. Frontend sanitization cannot prevent this because the file has already been read server-side.

A minimal vulnerable usage pattern is any page that forwards untrusted input into `ui.restructured_text()`, e.g. content taken from query parameters, form fields, or other user-controlled sources.

### Impact

Local file disclosure. An attacker who can supply reStructuredText content can read files accessible to the NiceGUI server process. Depending on deployment, this may expose:

- application `.env` files
- database URLs, API tokens, session/storage secrets
- OAuth or cloud credentials
- Docker or Kubernetes mounted secrets
- application source files
- logs and other process-readable files

The confirmed impact is confidentiality loss through arbitrary local file read. Applications are only impacted when they pass untrusted or user-controlled reStructuredText into `ui.restructured_text()`.

### Recommended fix

Disable unsafe Docutils features in `prepare_content()`:

```python
html = publish_parts(
    remove_indentation(content),
    writer_name='html4',
    settings_overrides={
        'syntax_highlight': 'short',
        'file_insertion_enabled': False,
        'raw_enabled': False,
        '_disable_config': True,
    },
)
```

This blocks the `include`, `csv-table :file:`, and `raw :file:` directives as well as local `docutils.conf` overrides.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-jfrm-rx66-g536
- https://nvd.nist.gov/vuln/detail/CVE-2026-45553
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.12.0
