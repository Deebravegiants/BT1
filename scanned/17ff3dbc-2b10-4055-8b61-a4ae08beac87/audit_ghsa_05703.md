# [M] Spree API has Authenticated Insecure Direct Object Reference (IDOR) via Order Modification

## Summary
Severity: Medium
Advisory: GHSA-g268-72p7-9j6j
CVE: CVE-2026-22588
CWE: CWE-639
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-g268-72p7-9j6j
Type: github-advisory

## Affected
- RubyGems: `spree_api` — affected >=3.7.0 <4.10.2
- RubyGems: `spree_api` — affected >=5.0.0 <5.0.7
- RubyGems: `spree_api` — affected >=5.1.0 <5.1.9
- RubyGems: `spree_api` — affected >=5.2.0 <5.2.5

## Details
### Summary
An Authenticated Insecure Direct Object Reference (IDOR) vulnerability was identified that allows an authenticated user to retrieve other users’ address information by modifying an existing order.
By editing an order they legitimately own and manipulating address identifiers in the request, the backend server accepts and processes references to addresses belonging to other users, subsequently associating those addresses with the attacker’s order and returning them in the response.

### Details
Affected Component(s)
- Authenticated user order management
- Address association logic
- Order update endpoint(s)
Affected Endpoint(s):
- `/api/v2/storefront/checkout`

The application fails to enforce proper object-level authorization when updating an existing order. While the user is authenticated and authorized to modify their own order, the backend does not verify that the supplied address identifiers belong to the same authenticated user.

### PoC
Preconditions
- Valid authenticated user account

Step 1: Log-in using a valid user, in this case customer2@example.com
Step 2: Visualize current user’s addresses 

**Request**
GET `/account/addresses`

The following screenshot shows customer2@example.com address. 

<img width="336" height="375" alt="User Address" src="https://github.com/user-attachments/assets/ceb1f214-7ac0-40b0-af22-6fe9d21254bb" />

Step 3: Initialize the Shopping Cart

**Request**
POST `/api/v2/storefront/cart HTTP/1.1`

From the response, extract the token marked in bold.

Step 4: Legitimate Order Edit Request

Using the obtained order token **A1cram_6cFWpoj4V1yPkuQ1767113871701** perform an edit order  request in order to add a custom billing address

**Request**
PATCH `/api/v2/storefront/checkout`

```json
{
    "include": "billing_address",
    "order": {
      "email": "idor_test@example.com",
      "bill_address_attributes": {
        "firstname":"CTF","lastname":"Tester","address1":"123 Main St",
        "city":"Andorra la Vella","zipcode":"AD100","country_iso":"AD"
      },
      "ship_address_attributes": {
        "firstname":"CTF","lastname":"Tester","address1":"123 Main St",
        "city":"Andorra la Vella","zipcode":"AD100","country_iso":"AD"
      }
    }
  }
```

Step 5: Modify the order request to include the other user's address and trigger the IDOR.

In this request, the attacker modifies the request by substituting the address identifier with one belonging to another user, thereby rendering the original address identifier accessible to the attacker.

**Request**
PATCH `/api/v2/storefront/checkout`

```json
{"include":"billing_address","order":**{"bill_address_attributes":{"id":1}}**}
```

As can be seen other user's address is displayed.

### Impact
As a result, an attacker can:

- Replace the address identifier with one belonging to another user
- Cause the backend to associate and return another user’s address within the attacker’s order

## References
- https://github.com/spree/spree/security/advisories/GHSA-g268-72p7-9j6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22588
- https://github.com/spree/spree/commit/02acabdce2c5f14fd687335b068d901a957a7e72
- https://github.com/spree/spree/commit/17e78a91b736b49dbea8d1bb1223c284383ee5f3
- https://github.com/spree/spree/commit/b409c0fd327e7ce37f63238894670d07079eefe8
- https://github.com/spree/spree/commit/d3f961c442e0015661535cbd6eb22475f76d2dc7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree_api/CVE-2026-22588.yml
- https://github.com/spree/spree
