# [M] Bref Doesn't Support Multiple Value Headers in ApiGatewayFormatV2

## Summary
Severity: Medium
Advisory: GHSA-99f9-gv72-fw9r
CVE: CVE-2024-24753
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-99f9-gv72-fw9r
Type: github-advisory

## Affected
- Packagist: `bref/bref` — affected >=0 <2.1.13

## Details
## Impacted Resources

bref/src/Event/Http/HttpResponse.php:61-90

## Description

When Bref is used in combination with an API Gateway with the v2 format, it does not handle multiple values headers.

Precisely, if PHP generates a response with two headers having the same key but different values only the latest one is kept.

## Impact

If an application relies on multiple headers with the same key being set for security reasons, then Bref would lower the application security.

For example, if an application sets multiple `Content-Security-Policy` headers, then Bref would just reflect the latest one.

## PoC

1. Create a new Bref project.
2. Create an `index.php` file with the following content:
```php
<?php
header("Content-Security-Policy: script-src 'none'", false);
header("Content-Security-Policy: img-src 'self'", false);
?>
<script>alert(document.domain)</script>
<img src="https://bref.sh/favicon-32x32.png">
```
3. Use the following `serverless.yml` to deploy the Lambda:
```yaml
service: app

provider:
    name: aws
    region: eu-central-1

plugins:
    - ./vendor/bref/bref

functions:
    api:
        handler: index.php
        description: ''
        runtime: php-81-fpm
        timeout: 28 # in seconds (API Gateway has a timeout of 29 seconds)
        events:
            -   httpApi: '*'

# Exclude files from deployment
package:
    patterns:
        - '!node_modules/**'
        - '!tests/**'
```
4. Browse the Lambda URL.
5. Notice that the JavaScript code is executed as the `Content-Security-Policy: script-src 'none'` header has been removed.
6. Notice that the external image has not been loaded as the `Content-Security-Policy: img-src 'self'` header has been kept.
7. Start a PHP server inside the project directory (e.g. `php -S 127.0.0.1:8090`).
8. Browse the `index.php` script through the PHP server (e.g. http://127.0.0.1:8090/index.php).
9. Notice that the JavaScript code is not executed as the `Content-Security-Policy: script-src 'none'` header has been kept.
10. Notice that the external image has not been loaded as the `Content-Security-Policy: img-src 'self'` header has been kept.

## Suggested Remediation

Concatenate all the multiple value headers' values with a comma (`,`) as separator and return a single header with all the values to the API Gateway.

## References

- https://www.rfc-editor.org/rfc/rfc9110.html#section-5.2

## References
- https://github.com/brefphp/bref/security/advisories/GHSA-99f9-gv72-fw9r
- https://nvd.nist.gov/vuln/detail/CVE-2024-24753
- https://github.com/brefphp/bref/commit/f834027aaf88b3885f4aa8edf6944ae920daf2dc
- https://github.com/brefphp/bref
- https://github.com/brefphp/bref/blob/2.1.12/src/Event/Http/HttpResponse.php#L61-L90
