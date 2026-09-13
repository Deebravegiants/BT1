# [M] oban_web missing authorization check on `save-job` event handler

## Summary
Severity: Medium
Advisory: GHSA-389x-rgxr-8m33
CVE: CVE-2026-48592
CWE: CWE-862
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-389x-rgxr-8m33
Type: github-advisory

## Affected
- Hex: `oban_web` — affected >=2.12.0 <2.12.5

## Details
### Summary

`oban_web` 2.12.0 through the current unpatched release exposes a `save-job` LiveView event handler that performs no authorization check, allowing any authenticated user (including those with `:read_only` access) to overwrite a queued job's `worker` field with any other `Oban.Worker` module present in the application. On the job's next execution attempt, Oban dispatches `perform/1` on the attacker-chosen module instead of the intended one.

### Details

In `lib/oban/web/live/jobs/detail_component.ex`, the sibling event handlers for destructive actions all gate their side effects via `can?/2` (cancel, delete, retry). The `handle_event("save-job", params, socket)` clause added in 2.12.0 has no equivalent guard. It builds a `changes` map from the client-supplied params (including `worker`, `queue`, `priority`, `max_attempts`, `scheduled_at`, `tags`, `args`) and unconditionally dispatches `{:update_job, job, changes}` to the parent LiveView, which writes the changes to the database.

The `disabled` attribute on the edit fieldset and button in the rendered HTML is advisory only. The Phoenix LiveView channel dispatches any `phx-event` pushed over the authenticated WebSocket regardless of what the DOM looks like, so the attacker pushes the event directly over the WebSocket without touching the UI.

The attacker is constrained to substituting an existing `Oban.Worker` module already loaded in the application (no code injection). The impact depends on what workers are available in the target application.

### PoC

1. Obtain an authenticated session with at minimum `:read_only` access to the Oban.Web dashboard.
2. Open any job's detail panel to obtain its job ID.
3. Push a forged `save-job` event over the LiveView WebSocket with `"worker"` set to the desired target module name.
4. The server accepts the payload and updates the job row. On its next execution attempt, Oban invokes `perform/1` on the attacker-chosen module.

### Impact

CVSS 4.0 score 5.3 (Medium). Any application running `oban_web` >= 2.12.0 that exposes the dashboard to users with less than full job-management privileges is affected. The only precondition is an authenticated session with `:read_only` access or higher.

## References

* Introduction commit: https://github.com/oban-bg/oban_web/commit/a17bc8c31286c9d516e2892cf5483d1c95e65d6c
* Patch commit: https://github.com/oban-bg/oban_web/commit/ab3c5d1d3eba06c62045f16f2cd7781c7752e248

## References
- https://github.com/oban-bg/oban_web/security/advisories/GHSA-389x-rgxr-8m33
- https://nvd.nist.gov/vuln/detail/CVE-2026-48592
- https://github.com/oban-bg/oban_web/commit/ab3c5d1d3eba06c62045f16f2cd7781c7752e248
- https://cna.erlef.org/cves/CVE-2026-48592.html
- https://github.com/oban-bg/oban_web
- https://osv.dev/vulnerability/EEF-CVE-2026-48592
