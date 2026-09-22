# [H] Open WebUI: Low-privilege authenticated users can enumerate and stop global background tasks, causing system-wide chat disruption

## Summary
Severity: High
Advisory: GHSA-8jjp-r2w2-4v22
CVE: CVE-2026-45399
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-8jjp-r2w2-4v22
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
### Summary
Any authenticated user with low privileges can enumerate active background tasks across the system and stop tasks belonging to other users via the GET /api/tasks and POST /api/tasks/stop/{task_id} methods. This allows a casual user to disrupt system-wide chat usage by continuously canceling other users' active tasks. This is a real authorization vulnerability affecting integrity and usability in multi-user deployments.


### Details
Open WebUI exposes `GET /api/tasks` and `POST /api/tasks/stop/{task_id}` to any verified user. These endpoints operate on a global task namespace and accept raw `task_id` values without checking whether the task belongs to the current caller.

As a result, a normal authenticated user can enumerate active global task IDs and stop tasks belonging to other users.

Root cause:

1. Route authorization is too weak.

In `backend/open_webui/main.py`, both endpoints only require `get_verified_user`:

```python
@app.post('/api/tasks/stop/{task_id}')
async def stop_task_endpoint(request: Request, task_id: str, user=Depends(get_verified_user)):
    result = await stop_task(request.app.state.redis, task_id)

@app.get('/api/tasks')
async def list_tasks_endpoint(request: Request, user=Depends(get_verified_user)):
    return {'tasks': await list_tasks(request.app.state.redis)}
```

`get_verified_user` accepts both `user` and `admin` roles in `backend/open_webui/utils/auth.py`.

2. The helper operates on a global namespace.

In `backend/open_webui/tasks.py`, task listing is global:

```python
async def list_tasks(redis):
    if redis:
        return await redis_list_tasks(redis)
    return list(tasks.keys())
```

In `backend/open_webui/tasks.py`, task stopping is by raw `task_id`:

```python
async def stop_task(redis, task_id: str):
    if redis:
        item_id = await redis.hget(REDIS_TASKS_KEY, task_id)
        await redis_send_command(redis, {'action': 'stop', 'task_id': task_id})
        await redis_cleanup_task(redis, task_id, item_id or None)
```

There is no owner check, no `user_id` check, and no mapping from `task_id` back to the current caller before stop or cleanup.

This also appears unintended because the codebase already has a scoped route, `GET /api/tasks/chat/{chat_id}`, which checks whether the chat belongs to the current user before returning task IDs.

Relevant code references:
- `backend/open_webui/main.py:1975`
- `backend/open_webui/main.py:1984`
- `backend/open_webui/main.py:1989`
- `backend/open_webui/tasks.py:127`
- `backend/open_webui/tasks.py:145`
- `backend/open_webui/utils/auth.py:415`

Suggested remediation:
- Store task ownership metadata such as `user_id` and `chat_id`, then enforce owner-only access for non-admin users
- Suggested implementation locations:
  - `backend/open_webui/main.py`: add authentication checks for `/api/tasks` and `/api/tasks/stop/{task_id}`
  - `backend/open_webui/tasks.py`: add support for storing/querying task ownership metadata such as `user_id` and `chat_id`, and support owner-scoped listing/stopping



### PoC
Preconditions:

- Default `main` branch deployment
- Authentication enabled
- Two normal user accounts, or any multi-user deployment where the attacker has one authenticated non-admin account
- At least one task actively running for another user

This does not require any weakened security settings.

PoC objective:

1. Show that a non-admin user can see global active task IDs that are not their own
2. Show that the same user can stop another user's active task

Reproduction steps:

#### Step 1. Victim starts a long-running task

Using the UI, User A starts a long response generation or another background task and leaves it running.

Expected security model:
User B should not be able to see or control User A's task.

#### Step 2. Attacker enumerates global task IDs

Using User B's authenticated token:

```bash
curl -i -H "Authorization: Bearer <USER_B_TOKEN>" http://<open-webui-host>/api/tasks
```

Expected result:

- only User B's own task IDs should be returned, or
- the endpoint should be admin-only

Actual result:
the response returns the global active task list.

Example response shape:

```json
{"tasks":["<task-id-a>","<task-id-b>"]}
```

This exposes task IDs belonging to other users.

#### Step 3. Attacker stops a foreign task

Pick a task ID that belongs to User A and send:

```bash
curl -i -X POST -H "Authorization: Bearer <USER_B_TOKEN>" http://<open-webui-host>/api/tasks/stop/<FOREIGN_TASK_ID>
```

Expected result:

- `403 Forbidden`, or
- `404 Not Found` for non-owned tasks, or
- admin-only access

Actual result:
the server accepts the request and attempts to stop the foreign task.

Example response shape:

```json
{"status":true,"message":"Task <FOREIGN_TASK_ID> stopped."}
```

#### Step 4. Observe boundary violation

User A's running task is interrupted or disappears from the active task set even though User B does not own it.

What actions become possible that should not be possible:

- enumerate globally active task IDs across users
- cancel another user's in-progress generation or background work
- repeat this for every returned task ID, causing broad cross-user disruption

Copy-paste PoC summary:

1. Enumerate all active tasks as a normal non-admin user

```bash
curl -s -H "Authorization: Bearer <USER_B_TOKEN>" http://<open-webui-host>/api/tasks
```

2. Stop a task that does not belong to that user

```bash
curl -s -X POST -H "Authorization: Bearer <USER_B_TOKEN>" http://<open-webui-host>/api/tasks/stop/<FOREIGN_TASK_ID>
```

### Impact
Type of vulnerability:
broken object-level authorization affecting a global runtime control-plane endpoint.

Who is impacted:

- all users in a multi-user Open WebUI deployment
- any user currently running a background task, especially chat generation tasks
- administrators indirectly, because normal users can disrupt system-wide usage without admin privileges

Direct impact:

- cross-user task ID disclosure
- cross-user task cancellation

Practical impact:

- interruption of long-running chat responses
- interruption of background indexing or ingestion tasks associated with shared runtime jobs
- one ordinary authenticated low-privilege user can continuously poll `/api/tasks` and immediately cancel every newly created active task
- with a simple loop or script, this becomes a practical persistent denial-of-service against chat usage for all users on the instance
- in a multi-user deployment, normal users may be unable to complete any chat generation while the attacker continues polling and cancelling tasks

Why severity is meaningful:

- privileges required: low, only an authenticated non-admin account
- scope: cross-user
- impact class: integrity and availability
- exploitation complexity: low once logged in

This is not full account takeover or privilege escalation, but it enables platform-wide operational disruption from a low-privilege account. In practice, sustained exploitation can make chat functionality effectively unusable for other users on the system.

## Resolution

Fixed in commit [e7ff4768f](https://github.com/open-webui/open-webui/commit/e7ff4768f8ffe1924b4576381c9e45e8a64350e4) ([#23454](https://github.com/open-webui/open-webui/pull/23454), "Add ownership checks to global task endpoints"), first released in **v0.9.0** (Apr 2026).

The fix takes a simpler approach than per-task ownership tracking, which would have required a schema change to attribute every task to a `user_id`:

- `GET /api/tasks` and `POST /api/tasks/stop/{task_id}` are restricted to admin-only via `Depends(get_admin_user)`. Cross-user enumeration and termination are no longer reachable from a non-admin account.
- A new scoped `POST /api/tasks/chat/{chat_id}/stop` endpoint covers the legitimate non-admin use case (a user stopping their own in-progress generation), reusing the same chat-ownership check the existing `GET /api/tasks/chat/{chat_id}` already enforces.

CVE-2025-63681 was a prior disclosure of the same authorization gap against v0.6.33; the fix in v0.9.0 also resolves that.

Users on `>= 0.9.0` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8jjp-r2w2-4v22
- https://nvd.nist.gov/vuln/detail/CVE-2026-45399
- https://github.com/open-webui/open-webui/pull/23454
- https://github.com/open-webui/open-webui/commit/e7ff4768f8ffe1924b4576381c9e45e8a64350e4
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0
