# [H] Pimcore Has an Incomplete Patch for CVE-2023-30848

## Summary
Severity: High
Advisory: GHSA-qvr7-7g55-69xj
CVE: CVE-2026-23492
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-qvr7-7g55-69xj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.1
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.14

## Details
### Summary
An **incomplete SQL injection patch** in the Admin Search Find API allows an authenticated attacker to perform **blind SQL injection**.
Although CVE-2023-30848 attempted to mitigate SQL injection by removing SQL comments (--) and catching syntax errors, the fix is insufficient. Attackers can still inject SQL payloads that do not rely on comments and infer database information via blind techniques. This vulnerability affects the admin interface and can lead to **database information disclosure**.

### Details
The vulnerability exists in the Admin Search Find API endpoint:
```
/admin/search/search/find
```
In CVE-2023-30848, the following patch was applied:

- SQL comments are removed by replacing `--`
- SQL syntax errors are caught and replaced with a generic exception

Relevant commit:  
https://github.com/pimcore/pimcore/commit/25ad8674886f2b938243cbe13e33e204a2e35cc3

Key changes include:
```
// remove sql comments
$fields = str_replace('--', '', $fields);

try {
    $hits = $searcherList->load();
} catch (SyntaxErrorException $syntaxErrorException) {
    throw new \InvalidArgumentException('Check your arguments.');
}
```
However, this mitigation is incomplete for the following reasons:

**1. Only `--` is filtered**

SQL injection does not require SQL comments. Payloads using boolean conditions, SQL functions, or time-based expressions remain effective.

**2. Exception handling only suppresses error output**

While syntax errors no longer produce detailed error messages, the underlying SQL query is still executed. This allows attackers to perform blind SQL injection.

**3. User-controlled input is still used in SQL query construction**
The `fields[]` parameter is attacker-controlled and can be abused to inject SQL expressions into the generated query.

As a result, attackers can craft payloads that do not trigger syntax errors and still influence SQL execution.
### PoC
The following request demonstrates a **blind SQL injection** via the `fields[]` parameter.

**Boolean-based Blind Injection**
```
GET /admin/search/search/find?query=2&
fields[]=field1 AND (SELECT CASE WHEN (1=1) THEN 1 ELSE 0 END)=1~field2&
filter=[{"property":"value"}]&
class=classname
```
**Time-based Blind Injection**
```
GET /admin/search/search/find?query=2&
fields[]=field1 AND IF(1=1,SLEEP(5),0)~field2&
filter=[{"property":"value"}]&
class=classname
```
**Observed behavior:**

- When the condition is true, the response is delayed (e.g., ~5 seconds)

- When the condition is false, the response is returned immediately

This confirms that injected SQL expressions are executed successfully.
### Impact
This is a **Blind SQL Injection vulnerability.**

- Affected users: Systems exposing the Admin Search Find API to authenticated users

- Attack requirements: Authenticated access to the admin interface

- Potential impact:

  - Database schema enumeration
  
  - Extraction of sensitive data via blind SQL injection
  
  - Potential full database compromise depending on database privileges

This issue demonstrates that the fix for CVE-2023-30848 is **incomplete.**

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-qvr7-7g55-69xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-23492
- https://github.com/pimcore/pimcore/commit/25ad8674886f2b938243cbe13e33e204a2e35cc3
- https://github.com/advisories/GHSA-6mhm-gcpf-5gr8
- https://github.com/pimcore/pimcore
