# [H] lgsl Stored Cross-Site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-xx95-62h6-h7v3
CVE: CVE-2024-56361
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-12-26
Source: https://github.com/advisories/GHSA-xx95-62h6-h7v3
Type: github-advisory

## Affected
- Packagist: `tltneon/lgsl` — affected >=0 <7.0.0

## Details
### Summary

A stored cross-site scripting (XSS) vulnerability was identified in lgsl. The issue arises from improper sanitation of user input. Everyone who accesses this page will be affected by this attack.

### Details

The function `lgsl_query_40` in `lgsl_protocol.php` has implemented an HTTP crawler. This function makes a request to the registered game server, and upon crawling the malicious `/info` endpoint with our payload, will render our javascript on the info page. This information is being displayed via `lgsl_details.php`

#### Affected Code:
```php
      foreach ($server['e'] as $field => $value) {
        $value = preg_replace('/((https*:\/\/|https*:\/\/www\.|www\.)[\w\d\.\-\/=$?​]*)/i', "<a href='$1' target='_blank'>$1</a>", html_entity_decode($value));
        $output .= "
        <tr><td> {$field} </td><td> {$value} </td></tr>";
      }
```
### PoC

1. Create a game server with type `eco` and set the target host and port accordingly to your ttack server. I have crafted this json payload that is being parsed according to the schema and being served on `/info` 

2. Serve the following JSON payload at `/info` on your handler
```json
{
  "Animals": "1",
  "EconomyDesc": "<img src=x onerror=prompt(1)>"
}
```
3. Access the corresponding server info page at `/s?=`. Upon refreshing & crawling our server, it should execute our javascript.

## References
- https://github.com/tltneon/lgsl/security/advisories/GHSA-xx95-62h6-h7v3
- https://github.com/tltneon/lgsl/commit/3fbd3bb581b636f7fd3ea0592c5f8df87d3a2843
- https://github.com/tltneon/lgsl
