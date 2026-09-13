# [M] Paymenter has race condition in payWithCredit() that enables credit double-spend

## Summary
Severity: Medium
Advisory: GHSA-pgcq-8grm-5rx9
CVE: CVE-2026-55219
CWE: CWE-362
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-pgcq-8grm-5rx9
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.5.5

## Details
### Summary
The credit payment implementation in `app/Livewire/Invoices/Show.php` executes a pessimistic row lock (`lockForUpdate()`) outside of an active database transaction. Because MySQL/MariaDB requires an enclosing transaction to enforce row-level locks, the guard is ineffective. Concurrent payment requests can exploit this race condition to read the same credit balance simultaneously, allowing users to pay multiple invoices using the same credit balance.

### Technical Details
The issue occurs because the application attempts to lock the user's credit balance row in the database (`lockForUpdate()`) without opening a database transaction. In database systems like MySQL, a row lock only works inside a formal transaction; without one, the lock is completely ignored.

Because there is no active lock, two payment requests sent at the exact same millisecond can look at the database at the same time. Both requests see the original credit balance, decide it is sufficient, and approve the payment.

### Impact
This race condition allows any authenticated user with a valid credit balance to bypass balance restrictions and settle multiple pending invoices simultaneously for the cost of a single invoice.

Because the payment processes successfully through ExtensionHelper::addPayment(), the application provisions the corresponding services or digital goods, resulting in direct financial or resource loss to the platform.

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-pgcq-8grm-5rx9
- https://github.com/Paymenter/Paymenter
