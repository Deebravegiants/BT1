# [H] Graphite Has a Pickle Deserialization Vulnerability

## Summary
Severity: High
Advisory: GHSA-qw48-84f6-28gv
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-qw48-84f6-28gv
Type: github-advisory

## Affected
- PyPI: `graphitedb` — affected >=0 <0.2

## Details
### Impact
**Type of vulnerability:** Insecure Deserialization via Python's `pickle` module.

**Who is impacted:**  
Users of *Graphite graph database engine* versions **before 0.2** who load database files from untrusted or third-party sources.  
An attacker could craft a malicious database file that executes arbitrary code when loaded by the engine. This is possible because the engine used `pickle` for serialization, which is known to be unsafe for untrusted data.

### Patches
The vulnerability has been patched starting from **version 0.2**.  
All users should upgrade to **version 0.2 or later** (the current version is 0.4 at publishing time).  
In version 0.2 and above, the engine uses **JSON** instead of `pickle` for database storage, eliminating the deserialization risk.

### Workarounds
If users cannot upgrade immediately:

1. **Do not load database files from untrusted or unknown sources** when using versions <0.2.
2. **Migrate existing pickle-based databases** to the new JSON format using the provided migration module:

```python
from graphite.Migration import convert_pickle_to_json
convert_pickle_to_json("path/to/old_database.pkl", "path/to/new_database.json")
```

After migration, you can safely use the database with version 0.2+.

**Note:** Versions 0.2 and later will show a **warning** when attempting to load legacy pickle files, reminding you to migrate them. Also, **you can't load pickle files** in 0.2 and later.

### Resources
- Upgrade to [v0.2 or newer](https://github.com/mkh-user/graphite/releases)
- Migration guide: See `graphite.Migration` module documentation
- More on pickle security: [Python docs – pickle security](https://docs.python.org/3/library/pickle.html#module-pickle)

## References
- https://github.com/mkh-user/graphite/security/advisories/GHSA-qw48-84f6-28gv
- https://github.com/mkh-user/graphite
- https://github.com/mkh-user/graphite/releases/tag/v0.2
