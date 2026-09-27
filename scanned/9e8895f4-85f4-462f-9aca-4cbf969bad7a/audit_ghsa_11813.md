# [M] Kimai's API invoice endpoint missing customer-level access control (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-v33r-r6h2-8wr7
CVE: CVE-2026-28685
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-v33r-r6h2-8wr7
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.51.0

## Details
## Summary

`GET /api/invoices/{id}` only checks the role-based `view_invoice` permission but does not verify the requesting user has `access` to the invoice's customer. Any user with `ROLE_TEAMLEAD` (which grants `view_invoice`) can read all invoices in the system, including those belonging to customers assigned to other teams.

## Affected Code

`src/API/InvoiceController.php` line 92-101:

```php
#[IsGranted('view_invoice')]           // Role check only, no customer access check
#[Route(methods: ['GET'], path: '/{id}', name: 'get_invoice', requirements: ['id' => '\d+'])]
public function getAction(Invoice $invoice): Response
{
    $view = new View($invoice, 200);
    $view->getContext()->setGroups(self::GROUPS_ENTITY);
    return $this->viewHandler->handle($view);  // Returns ANY invoice by ID
}
```

The web controller (`src/Controller/InvoiceController.php` line 304-307) correctly checks customer access:

```php
#[IsGranted('view_invoice')]
#[IsGranted(new Expression("is_granted('access', subject.getCustomer())"), 'invoice')]
public function downloadAction(Invoice $invoice, ...): Response { ... }
```

The `access` attribute in `CustomerVoter` (line 71-87) verifies team membership, but this check is entirely missing from the API endpoint.

## PoC

Tested against Kimai v2.50.0 (Docker: `kimai/kimai2:apache`).

Setup:
- TeamA with CustomerA ("SecretCorp"), TeamB with CustomerB ("BobCorp")
- Bob is a teamlead in TeamB only
- An invoice exists for SecretCorp (TeamA)

```bash
# Bob (TeamB) reads SecretCorp (TeamA) invoice
curl -H "Authorization: Bearer BOB_TOKEN" http://localhost:8888/api/invoices/1
```

Response (200 OK):
```json
{
  "invoiceNumber": "INV-2026-001",
  "total": 15000.0,
  "currency": "USD",
  "customer": {"name": "SecretCorp", ...}
}
```

Bob can also enumerate all invoices via `GET /api/invoices` — the list endpoint uses `setCurrentUser()` in the query but the single-item endpoint bypasses this entirely via Symfony ParamConverter.

## Impact

Any teamlead can read all invoices across the system regardless of team assignment. Invoice data typically contains sensitive financial information (amounts, customer details, payment terms). In multi-team deployments this breaks the intended data isolation between teams.

## Suggested Fix

Add the customer access check to the API endpoint, matching the web controller:

```diff
 #[IsGranted('view_invoice')]
+#[IsGranted(new Expression("is_granted('access', subject.getCustomer())"), 'invoice')]
 #[Route(methods: ['GET'], path: '/{id}', name: 'get_invoice')]
 public function getAction(Invoice $invoice): Response
```

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-v33r-r6h2-8wr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-28685
- https://github.com/kimai/kimai/commit/a0601c8cb28fed1cca19051a8272425069ab758f
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.51.0
