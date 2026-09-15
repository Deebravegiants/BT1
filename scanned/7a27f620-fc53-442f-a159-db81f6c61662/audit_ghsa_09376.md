# [H] Pimcore Platform - SQL Injection in DataObject composite index handling during class definition import/save

## Summary
Severity: High
Advisory: GHSA-r2f4-ff2p-xc64
CVE: CVE-2026-5394
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-r2f4-ff2p-xc64
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.7
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.3

## Details
My name is Oscar Uribe, Security Researcher at Fluid Attacks. I am reaching out because we have identified a security vulnerability in Pimcore 12.3.3 that we would like to report to you so we can coordinate a responsible disclosure together.

As part of our standard disclosure measures, we follow a timeline (outlined at https://fluidattacks.com/advisories/policy), which is aligned with ISO/IEC 29147:2018 and ISO/IEC 30111:2019. In short, the timeline works as follows: we ask for acknowledgment of the report within a few days of your first accessing it, and from there, we are happy to coordinate a joint disclosure date with you, typically within 90 days of the initial discovery. This gives your team reasonable time to assess, develop, and release a fix.

We have reserved the CVE ID **"CVE-2026-5394"** for this issue, and the advisory will eventually be published at [https://fluidattacks.com/advisories/dragons](https://fluidattacks.com/advisories/dragons). We are committed to coordinating the timing of that publication with you.

Please feel free to reach out if you have any questions about the report, the process, or the timeline. We are glad to work with you on this.

## Description
An authenticated administrative user who can import or save DataObject class definitions can inject attacker-controlled composite index metadata and trigger unintended SQL execution in the backend.

The vulnerable flow accepts `compositeIndices` from imported JSON, stores the values without strict validation, and later concatenates them directly into `ALTER TABLE ... DROP INDEX` and `ALTER TABLE ... ADD INDEX` statements executed through Doctrine DBAL.

Although the original report focused on `compositeIndices.index_key`, independent code review shows that the strongest and most reliable injection point is `compositeIndices.index_columns`, because it is inserted verbatim inside the `ADD INDEX (...)` clause. This permits injection of additional `ALTER TABLE` subclauses against Pimcore object tables without relying on stacked queries.

## Vulnerability
### Root cause
1. Source:
   - `Pimcore\Model\DataObject\ClassDefinition\Service::importClassDefinitionFromJson()` accepts `compositeIndices` directly from imported JSON.
2. Assignment:
   - `Pimcore\Model\DataObject\ClassDefinition::setCompositeIndices()` does not enforce an allowlist for index names or column names.
   - The only special handling is a ManyToOne relation rewrite to `__id` and `__type`, which is not a security control.
3. Sink:
   - `Pimcore\Model\DataObject\Traits\CompositeIndexTrait::updateCompositeIndices()` builds raw SQL with string concatenation and executes it via `$this->db->executeQuery(...)`.
4. Missing protection:
   - `quoteIdentifier()` is used for the `SHOW INDEXES` query, but not for the dynamic `ALTER TABLE` statements.
   - No server-side schema validation restricts `index_key` or `index_columns` to known safe identifier characters.

### Confirmed source-to-sink path
1. `importClassDefinitionFromJson()` decodes attacker-controlled JSON and forwards `compositeIndices`.
2. `setCompositeIndices()` stores those values without sanitizing identifier content.
3. `ClassDefinition::save()` reaches `ClassDefinition\Dao::update()`.
4. `Dao::update()` calls `updateCompositeIndices()` for:
   - `object_store_<classId>`
   - `object_query_<classId>`
5. `Localizedfield\Dao` also calls `updateCompositeIndices()` for:
   - localized query tables
   - localized store tables

### Why this is exploitable
The vulnerable `ADD INDEX` statement is built as:

```php
'ALTER TABLE `'.$table.'` ADD INDEX `' . $key.'` ('.$columnName.');'
```

`$columnName` is produced from `implode(',', $columns)` and is not quoted or validated. A malicious `index_columns` element such as:

```text
slider), DROP COLUMN `oo_className` -- 
```

produces SQL of the form:

```sql
ALTER TABLE `object_query_<id>` ADD INDEX `c_poc_idx` (slider), DROP COLUMN `oo_className` -- );
```

This remains a single `ALTER TABLE` statement, so the base vulnerability does not depend on multi-statement support. The attacker can inject additional DDL clauses affecting the target Pimcore object table.

### Impact
The issue allows a privileged attacker to alter backend SQL behavior during class-definition import/save and modify schema on Pimcore object tables associated with the affected class.

Practical impact includes:
- unauthorized schema modification on object query/store tables
- backend denial of service by breaking expected table layout
- data integrity impact for DataObject storage and queries

`index_key` is also concatenated into SQL without proper identifier escaping, but the most defensible exploitation path is through `index_columns`.

Relevant code:
- `models/DataObject/ClassDefinition/Service.php:92-137`
- `models/DataObject/ClassDefinition.php:994-1006`
- `models/DataObject/Traits/CompositeIndexTrait.php:30-85`
- `models/DataObject/ClassDefinition/Dao.php:217-218`
- `models/DataObject/Localizedfield/Dao.php:945-951`

## PoC
### Application-level PoC
Preconditions:
- valid authenticated administrative session
- ability to import or save a class definition containing `compositeIndices`

The original report reproduced the issue through an authenticated Studio endpoint:

```http
POST /pimcore-studio/api/class/definition/configuration-view/detail/1/import
```

Minimal malicious JSON fragment:

```json
{
  "compositeIndices": [
    {
      "index_key": "poc_idx",
      "index_type": "query",
      "index_columns": [
        "slider), DROP COLUMN `oo_className` -- "
      ]
    }
  ]
}
```

Reproduction:
1. Authenticate as an administrator with permission to manage/import class definitions.
2. Export an existing class definition or prepare a valid class-definition JSON document.
3. Replace only the `compositeIndices` section with the payload above.
4. Import the modified definition or save the class through the administrative workflow.

Expected result:
- Pimcore reaches `updateCompositeIndices()` during class save/import.
- The backend executes an attacker-influenced `ALTER TABLE` statement against the target object table.
- The affected class table is modified unexpectedly, for example by dropping a column or otherwise changing schema.

### Minimal source-level confirmation
The behavior is directly visible from the code path:

```php
$newIndicesMap['c_' . $key] = implode(',', $columns);
$columnName = $newIndicesMap[$key];
$this->db->executeQuery(
    'ALTER TABLE `'.$table.'` ADD INDEX `' . $key.'` ('.$columnName.');'
);
```

No escaping or allowlist validation is applied to `$columns` before they are interpolated into SQL.

## Evidence of Exploitation

- Video of exploitation:

https://github.com/user-attachments/assets/64a49147-12a5-4550-ba22-cb4383523557

- Static evidence:

<img width="3004" height="1686" alt="Dragons-img" src="https://github.com/user-attachments/assets/2e920636-ce7e-4f8b-b80c-88fb3c4c5299" />

## Our security policy
We have reserved the ID CVE-2026-5394 to refer to this issue from now on.

[Disclosure policy](https://fluidattacks.com/advisories/policy)

## System Information
Pimcore Platform
Version `v12.3.3`
Database layer: `doctrine/dbal` `^4.4`
Operating System: Any

## References
Github Repository: https://github.com/pimcore/pimcore
Security: https://github.com/pimcore/pimcore/security

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-r2f4-ff2p-xc64
- https://nvd.nist.gov/vuln/detail/CVE-2026-5394
- https://github.com/pimcore/pimcore/pull/19108
- https://github.com/pimcore/pimcore/commit/6df625ff74015dc11f4bbe76170ce45bbd5dd61d
- https://fluidattacks.com/es/advisories/dragons
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.7
