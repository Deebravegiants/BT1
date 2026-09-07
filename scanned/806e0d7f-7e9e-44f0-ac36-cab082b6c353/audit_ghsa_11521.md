# [H] OliveTin Vulnerable to Unauthorized Action Output Disclosure via EventStream

## Summary
Severity: High
Advisory: GHSA-228v-wc5r-j8m7
CVE: CVE-2026-32102
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-228v-wc5r-j8m7
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <3000.10.2

## Details
### Summary

  OliveTin’s live EventStream broadcasts execution events and action output to authenticated dashboard subscribers without enforcing per-action authorization. A low-privileged authenticated user can receive output from actions they are
  not allowed to view, resulting in broken access control and sensitive information disclosure. I validated this on OliveTin 3000.10.2.




### Details
The issue is in the live event streaming path.

  EventStream() only checks whether the caller may access the dashboard, then registers the user as a stream subscriber:

  - service/internal/api/api.go:776

  After subscription, execution events are broadcast to all connected clients without checking whether each recipient is authorized to view logs for the action:

  - service/internal/api/api.go:846 OnExecutionStarted
  - service/internal/api/api.go:869 OnExecutionFinished
  - service/internal/api/api.go:1047 OnOutputChunk

  The event payload includes action output through:

  - service/internal/api/api.go:295 internalLogEntryToPb
  - service/internal/api/api.go:302 Output

  By contrast, the normal log APIs do apply per-action authorization checks:

  - service/internal/api/api.go:518 GetLogs
  - service/internal/api/api.go:585 GetActionLogs
  - service/internal/api/api.go:544 isLogEntryAllowed

  Root cause:

  - the subscription path enforces only coarse dashboard access
  - execution callbacks broadcast to every connected client
  - no per-recipient ACL check is applied before sending action metadata or output

  I validated the issue using:

  - an admin user with full ACLs
  - an alice user with no ACLs
  - a protected action that outputs TOPSECRET=alpha-bravo-charlie

  Despite having no relevant ACLs, alice still receives the ExecutionFinished event for the privileged action, including the protected output.



### PoC
Tested version:
```
  - 3000.10.2
```
  1. Fetch and check out 3000.10.2 in a clean worktree:
```bash
  git -C OliveTin fetch origin tag 3000.10.2
  git -C OliveTin worktree add /home/kali/CVE/OliveTin-3000.10.2 3000.10.2
```
  2. Copy the PoC test into the clean tree:
```bash
  cp OliveTin/service/internal/api/event_stream_leak_test.go \
    OliveTin-3000.10.2/service/internal/api/
```
  3. Run the targeted PoC test:
```bash
  cd OliveTin-3000.10.2/service
  go test ./internal/api -run TestEventStreamLeaksUnauthorizedExecutionOutput -count=1 -timeout 30s -v
```
  4. Optional: save validation output:
```bash
  go test ./internal/api -run TestEventStreamLeaksUnauthorizedExecutionOutput -count=1 -timeout 30s -v \
    2>&1 | tee /tmp/olivetin_eventstream_3000.10.2.log
```
  Observed validation output:
```bash
  === RUN   TestEventStreamLeaksUnauthorizedExecutionOutput
  time="2026-03-01T04:44:59-05:00" level=info msg="Action requested" actionTitle=secret-action tags="[]"
  time="2026-03-01T04:44:59-05:00" level=info msg="Action parse args - Before" actionTitle=secret-action cmd="echo 'TOPSECRET=alpha-bravo-charlie'"
  time="2026-03-01T04:44:59-05:00" level=info msg="Action parse args - After" actionTitle=secret-action cmd="echo 'TOPSECRET=alpha-bravo-charlie'"
  time="2026-03-01T04:44:59-05:00" level=info msg="Action started" actionTitle=secret-action timeout=1
  time="2026-03-01T04:44:59-05:00" level=info msg="Action finished" actionTitle=secret-action exit=0 outputLength=30 timedOut=false
  --- PASS: TestEventStreamLeaksUnauthorizedExecutionOutput (0.00s)
  PASS
  ok      github.com/OliveTin/OliveTin/internal/api       0.025s
```
  What this proves:

  - admin can execute the protected action
  - alice has no ACLs
  - alice still receives the streamed completion event for the protected action
  - protected action output is exposed through the event stream


### Impact
  This is an authenticated broken access control / information disclosure vulnerability.

  A low-privileged authenticated user can subscribe to EventStream and receive:

  - action execution metadata
  - execution tracking IDs
  - initiating username
  - live output chunks
  - final command output

  Who is impacted:

  - multi-user OliveTin deployments
  - environments where privileged actions produce secrets, tokens, internal system details, or other sensitive operational output
  - deployments where lower-privileged authenticated users can access the dashboard and subscribe to live events

  This bypasses intended per-action log/view restrictions for protected actions.

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-228v-wc5r-j8m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32102
- https://github.com/OliveTin/OliveTin
