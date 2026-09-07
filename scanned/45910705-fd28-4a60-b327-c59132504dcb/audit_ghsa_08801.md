# [H] netbox-data-flows has stored XSS in ObjectAlias names rendered inside DataFlow tables

## Summary
Severity: High
Advisory: GHSA-v7qw-hx66-4w9x
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-v7qw-hx66-4w9x
Type: github-advisory

## Affected
- PyPI: `netbox-data-flows` — affected >=0 <1.5.1

## Details
### Summary
An authenticated user who can create or edit `ObjectAlias` objects can store arbitrary HTML/JavaScript in an alias name. That payload is later rendered unescaped in `DataFlow` table views, causing a stored XSS when another user views the affected page.

### Details
The issue is caused by unsafe HTML generation in the plugin’s custom table column renderer.

Relevant code on `main` (`bf96eac`, same commit as `origin/main` at the time of review):

- `netbox_data_flows/models/objectaliases.py`
  - `ObjectAlias.name` is user-controlled (`CharField`)
  - `ObjectAlias.__str__()` returns `self.name` directly
- `netbox_data_flows/tables/dataflows.py`
  - `DataFlowTable.sources` and `DataFlowTable.destinations` use `ObjectAliasListColumn`
- `netbox_data_flows/tables/columns.py`
  - `ObjectAliasListColumn.render()` calls `object_list_to_string(value.all(), linkify=True)`
- `netbox_data_flows/utils/helpers.py`
  - `object_list_to_string()` builds raw anchor tags with:
    ```python
    mark_safe(separator.join(f'<a href="{o.get_absolute_url()}">{o}</a>' for o in objects))
    ```

The alias text (`{o}`) is inserted into HTML without escaping, then the whole string is marked safe. Because `ObjectAlias.__str__()` returns the user-supplied name, HTML/JS in the alias name is executed in the victim’s browser.

This affects any page rendering `DataFlowTable`, including at least:
- the main Data Flow list page
- model tabs that reuse `DataFlowTable`

### PoC
Environment:
- NetBox with `netbox-data-flows` installed
- No special plugin configuration required

Steps:
1. Log in as a user with permission to create or edit `ObjectAlias` and `DataFlow`.
2. Create a new `ObjectAlias` with the following name:
   ```html
   <img src=x onerror=alert(document.domain)>
   ```
3. Create or edit a `DataFlow` so this alias is present in either `sources` or `destinations`.
4. Log in as another user and open the Data Flow list page in the plugin UI.
5. The JavaScript executes when the table renders the alias list.

A simple path to trigger is the Data Flow list page. Any other page that renders `DataFlowTable` should also be tested.

### Impact
This is a stored cross-site scripting vulnerability.

Impacted users:
- any authenticated user who can view a page rendering the affected `DataFlow` table
- especially higher-privileged NetBox users, because an attacker with lower privileges may target them by planting a malicious alias name

Possible impact:
- session theft
- execution of privileged actions in the victim’s session
- exfiltration of data visible to the victim in NetBox

## References
- https://github.com/Alef-Burzmali/netbox-data-flows/security/advisories/GHSA-v7qw-hx66-4w9x
- https://github.com/Alef-Burzmali/netbox-data-flows
