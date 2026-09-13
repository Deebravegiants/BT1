# [M] Open WebUI: Tool source code disclosed to read-only users via the tool list and get endpoints

## Summary
Severity: Medium
Advisory: GHSA-3r7g-q6cg-q2vx
CVE: CVE-2026-70491
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-3r7g-q6cg-q2vx
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.11.0

## Details
## Summary

A workspace tool shared with a read grant returned its full Python source to the recipient. Any authenticated non-admin who could use a shared tool could also read its source, including any user on the instance when a tool was shared publicly. Source is meant to be a writer-only tier: the list response schema deliberately omits it and source export sits behind its own permission. The read endpoints delivered it anyway.

## Preconditions

- Authentication enabled (`WEBUI_AUTH=true`, default) and plugins enabled (`ENABLE_PLUGINS=true`, default).
- The attacker is an authenticated non-admin without the `workspace.tools` permission and without a write grant on the tool.
- A tool is shared with a read grant to the attacker, to one of their groups, or to all users (`user:*`).

Deployments that share no tools, or share them only with users who already hold write access, are not affected.

## Impact

A non-admin obtains another user's server-side tool source. Tool source commonly embeds hard-coded API keys, credentials and internal service URLs, so the practical loss frequently extends past the code itself. The attack needs no special permission beyond an ordinary account that a tool was shared with, and no user interaction. Confidentiality only: it grants no ability to create, modify or execute tools, and no integrity or availability impact.

## Fix

Fixed in 0.11.0 by commit `c05de13b4` (#27005) together with `310ae9130`. The per-id endpoint now drops the source for callers without write access, and the two list endpoints no longer load source at all. Function specs stay visible to read users, since the chat tool listing renders a tool's functions from them. Tool execution loads source server-side, so shared tools keep working. Upgrading to 0.11.0 fully resolves the issue with no configuration change.

## Root cause

Affected components: `GET /api/v1/tools/`, `GET /api/v1/tools/list` and `GET /api/v1/tools/id/{id}` in `backend/open_webui/routers/tools.py`, and the response models in `backend/open_webui/models/tools.py`. Every build carrying the plugin routes is affected.

`ToolResponse` deliberately omits the source and the specs, but its subclass `ToolUserResponse` permits extra fields, and each handler built its response by spreading a full dump of the tool model. The omitted fields were re-admitted as extras and serialised back to the caller, so the schema meant to enforce the writer-only tier enforced nothing at all. The listing path carried a second, independent defect: the flag that was supposed to keep source out of listings never changed the query it guarded.

## Proof of concept

Against a default instance on 0.10.2, with an admin account and a second account of role `user`:

1. As the admin, create a tool whose source contains a marker secret and share it read-only with everyone:

```
POST /api/v1/tools/create
{"id": "poctool",
 "name": "PoC Tool",
 "content": "API_KEY = \"TOOL_SRC_SECRET\"\nclass Tools:\n    def hello(self) -> str: return 'hi'",
 "meta": {"description": "poc"},
 "access_grants": [{"principal_type": "user", "principal_id": "*", "permission": "read"}]}
```

2. As the non-admin, call any of the three read endpoints:

```
GET /api/v1/tools/list
-> 200, item "poctool": write_access=false, content="API_KEY = \"TOOL_SRC_SECRET\" ..."
```

The same source is returned by `GET /api/v1/tools/` and `GET /api/v1/tools/id/poctool`. On 0.11.0 the identical run returns the item with no source for the non-admin, while the owner still receives it.

## Credits

- bogdancherniy11-sudo — reported the disclosure across the three tool read endpoints.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3r7g-q6cg-q2vx
- https://github.com/open-webui/open-webui/pull/27005
- https://github.com/open-webui/open-webui/commit/c05de13b4fca1ac8a17153782b46b3d0aacf491c
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
