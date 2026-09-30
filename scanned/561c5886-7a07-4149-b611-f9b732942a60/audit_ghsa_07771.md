# [H] LibreNMS: SQL Injection in ajax_table.php spreads through a covert data stream.

## Summary
Severity: High
Advisory: GHSA-h3rv-q4rq-pqcv
CVE: CVE-2026-26988
CWE: CWE-89
Ecosystem: Packagist
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-h3rv-q4rq-pqcv
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.2.0

## Details
### Summary
*SQL Injection in IPv6 Address Search functionality via `address` parameter**

A SQL injection vulnerability exists in the `ajax_table.php` endpoint. The application fails to properly sanitize or parameterize user input when processing IPv6 address searches. Specifically, the `address` parameter is split into an address and a prefix, and the prefix portion is directly concatenated into the SQL query string without validation. This allows an attacker to inject arbitrary SQL commands, potentially leading to unauthorized data access or database manipulation.

### Details
The vulnerability is located in the logic that handles address searching when `search_type` is set to `ipv6`.

The application takes the user-supplied `address` parameter and splits it using the `/` delimiter:
```PHP
[$address, $prefix] = explode('/', $vars['address']);
```
If the search_type is ipv6 and the $prefix variable is not empty, the code constructs the SQL query by directly concatenating the $prefix variable into the string:
```
} elseif ($vars['search_type'] == 'ipv6') {
    // ... code omitted ...
    if (! empty($prefix)) {
        // VULNERABILITY: Direct concatenation of user input
        $sql .= " AND ipv6_prefixlen = '$prefix'";
    }
}
```
Unlike the ipv4 block, which attempts to use prepared statements (binding parameters via $param[]), the ipv6 block treats the prefix as a raw string. By supplying an input containing a /, an attacker can populate the $prefix variable. If this variable contains single quotes ('), it breaks out of the string literal in the SQL statement, enabling SQL injection.

Vulnerable Code Snippet:
```
if (! empty($prefix)) {
    $sql .= " AND ipv6_prefixlen = '$prefix'";
}
```
### PoC
To reproduce this vulnerability, an attacker can send a specially crafted HTTP POST request to the ajax_table.php endpoint.

Payload breakdown:

- search_type=ipv6: Forces the execution flow into the vulnerable elseif block.

- address=snow/1nd'":

  - The explode function splits this into $address = 'snow' and $prefix = "1nd'"".

  - The SQL query becomes: ... AND ipv6_prefixlen = '1nd'"'.

  - The single quote ' closes the string definition in the SQL query, and the subsequent characters allow for SQL syntax manipulation.

Reproduction Steps:

1. Access the application instance.

2. Send the following request (adjusting the host as necessary):
```
POST /ajax_table.php HTTP/1.1
Host: localhost
id=address-search&search_type=ipv6&address=snow/1nd'" 
```
### Impact
This vulnerability allows an attacker to execute arbitrary SQL queries against the database.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-h3rv-q4rq-pqcv
- https://github.com/librenms/librenms/pull/18777
- https://github.com/librenms/librenms/commit/15429580baba03ed1dd377bada1bde4b7a1175a1
- https://github.com/librenms/librenms
