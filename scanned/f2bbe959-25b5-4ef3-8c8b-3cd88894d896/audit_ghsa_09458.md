# [M] PyLoad vulnerable to unauthenticated traceback disclosure via global exception handler in WebUI

## Summary
Severity: Medium
Advisory: GHSA-c3gc-9pf2-84gg
CVE: CVE-2026-44226
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-c3gc-9pf2-84gg
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev100

## Details
### Summary
`pyload-ng` WebUI returns full Python traceback details to clients on unhandled exceptions.

Because `/web/<path:filename>` is reachable without authentication and renders attacker-controlled template names, an unauthenticated user can reliably trigger a server exception (for example by requesting a non-existent template) and receive internal stack traces in the HTTP response.

### Details
The issue is caused by the combination of:

1. Unauthenticated template-render route:
- `src/pyload/webui/app/blueprints/app_blueprint.py:32-36`
  - `@bp.route("/web/<path:filename>", endpoint="web")`
  - `data = render_template(filename)` with user-controlled `filename`
  - no `@login_required(...)` on this route

2. Global exception handler exposes traceback to response:
- `src/pyload/webui/app/handlers.py:14-27`
  - `tb = traceback.format_exc()`
  - `messages.extend(tb.split('\n'))`
  - returned in rendered error page for all exceptions

3. Error page renders all `messages`:
- `src/pyload/webui/app/themes/modern/templates/base.html:217-219`
  - loops over `messages` and prints them in response HTML

So any unhandled exception can disclose internal implementation details (stack frames, source paths, exception metadata) to remote unauthenticated clients. 

This is a core behavior issue in default WebUI error handling

### PoC
```python
#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import tempfile
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "pyload" / "src" / "pyload"


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def route_has_no_login_required(app_blueprint: str) -> bool:
    m = re.search(
        r'@bp\\.route\\("/web/<path:filename>", endpoint="web"\\)\\s*'
        r"def render\\(filename\\):(?P<body>.*?)(?:\\n\\n@bp\\.route|\\Z)",
        app_blueprint,
        re.DOTALL,
    )
    if not m:
        return False
    block_start = max(0, m.start() - 200)
    block = app_blueprint[block_start:m.end()]
    return "@login_required(" not in block


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="pyload-traceback-infoleak-"))
    try:
        app_blueprint = read_text("webui/app/blueprints/app_blueprint.py")
        handlers = read_text("webui/app/handlers.py")
        base_template = read_text("webui/app/themes/modern/templates/base.html")

        unauth_web_route = '/web/<path:filename>' in app_blueprint and route_has_no_login_required(app_blueprint)
        user_controlled_template_name = "render_template(filename)" in app_blueprint
        handler_uses_traceback = "traceback.format_exc()" in handlers
        handler_appends_trace = "messages.extend(tb.split('\\n'))" in handlers
        global_exception_handler = "(Exception, handle_exception_error)" in handlers
        template_renders_messages = "{% for message in messages %}" in base_template and "{{message}}" in base_template

        leaked_traceback_keyword = False
        leaked_exception_type = False
        try:
            raise RuntimeError("forced-poc-error")
        except Exception:
            tb = traceback.format_exc()
            messages = [f"Error 500: forced-poc-error"]
            messages.extend(tb.split("\\n"))
            joined = "\\n".join(messages)
            leaked_traceback_keyword = "Traceback (most recent call last)" in joined
            leaked_exception_type = "RuntimeError: forced-poc-error" in joined

        repro_success = all(
            [
                unauth_web_route,
                user_controlled_template_name,
                handler_uses_traceback,
                handler_appends_trace,
                global_exception_handler,
                template_renders_messages,
                leaked_traceback_keyword,
                leaked_exception_type,
            ]
        )

        print("unauth_web_route=", unauth_web_route)
        print("user_controlled_template_name=", user_controlled_template_name)
        print("handler_uses_traceback=", handler_uses_traceback)
        print("handler_appends_trace=", handler_appends_trace)
        print("global_exception_handler=", global_exception_handler)
        print("template_renders_messages=", template_renders_messages)
        print("leaked_traceback_keyword=", leaked_traceback_keyword)
        print("leaked_exception_type=", leaked_exception_type)
        print("traceback_infoleak_repro_success=", repro_success)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        print("cleanup_done=True")


if __name__ == "__main__":
    main()
```

Observed result:
```text
unauth_web_route= True
user_controlled_template_name= True
handler_uses_traceback= True
handler_appends_trace= True
global_exception_handler= True
template_renders_messages= True
leaked_traceback_keyword= True
leaked_exception_type= True
traceback_infoleak_repro_success= True
cleanup_done=True
```

### Impact
- Vulnerability type: Information disclosure (stack trace / internal path leakage).
- Attack surface: unauthenticated WebUI request path.
- Exposes internal error details that help attackers map application internals and improve exploit reliability for follow-on attacks.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-c3gc-9pf2-84gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44226
- https://github.com/pyload/pyload
