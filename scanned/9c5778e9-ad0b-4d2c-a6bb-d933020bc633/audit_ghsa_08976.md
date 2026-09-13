# [M] Kimai vulnerable to formula Injection via tag names in XLSX export

## Summary
Severity: Medium
Advisory: GHSA-3xc2-h5r3-wv3r
CVE: CVE-2026-42267
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3xc2-h5r3-wv3r
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=2.27.0 <2.54.0

## Details
## Summary

Any `ROLE_USER` can create a tag with a formula string as its name (e.g. `=SUM(54+51)`) via `POST /api/tags` and assign it to a timesheet. When an admin exports timesheets to XLSX, `ArrayFormatter.formatValue()` joins tag names with `implode()` and returns the result unchanged. OpenSpout promotes any `=`-prefixed string to a `FormulaCell`, writing `<f>SUM(54+51)</f>` into the XLSX archive. Excel evaluates the formula when the file is opened.

## Details

### 1. `ArrayFormatter` does not sanitize before returning

`sanitizeDDE()` exists on `StringHelper` and is called by `TextFormatter`, but `ArrayFormatter` never calls it.
```php
// src/Export/Package/CellFormatter/ArrayFormatter.php:24
return implode(', ', $value);  // no sanitizeDDE() call
```

### 2. Tag name validation does not block formula trigger characters

The API blocks commas in tag names but permits `=`, `+`, `-`, and `@` - all valid formula prefixes in Excel and LibreOffice Calc.

### 3. OpenSpout silently promotes strings to formula cells

`Cell::fromValue("=SUM(54+51)")` returns a `FormulaCell` with no warning.

### PoC

1. It logs in as normal user, creates tag `=SUM(54+51)`, assigns it to a timesheet.
2. Admin has to export timesheets to Excel version via `/en/export/` endpoint.

<img width="1339" height="700" alt="image" src="https://github.com/user-attachments/assets/884c7943-5e3b-4647-8bcc-e264d6719d66" />

<img width="1304" height="128" alt="formula_injection_tags" src="https://github.com/user-attachments/assets/ef28f2ad-7491-4a15-bb18-1fcd6ff5e55a" />

## Impact

- Any `ROLE_USER` can plant a formula that executes on the workstation of any user who exports and opens timesheet data
- A single malicious tag poisons all future exports across all users and date ranges until the tag is deleted

## Fixes

1. Prevent `=` being part of the tag name (and other fields as well)
2. Use OpenSpout `TextCell` for everything that is a string

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-3xc2-h5r3-wv3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42267
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.54.0
