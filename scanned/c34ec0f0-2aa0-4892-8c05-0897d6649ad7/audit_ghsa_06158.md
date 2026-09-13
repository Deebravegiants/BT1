# [H] elFinder: SSRF protection bypass via DNS rebinding in the `fsock_get_contents()` fallback

## Summary
Severity: High
Advisory: GHSA-8x3q-jpjh-qh5c
CVE: CVE-2026-81889
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-8x3q-jpjh-qh5c
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.70

## Details
[poc.zip](https://github.com/user-attachments/files/30352020/poc.zip)
## Summary

elFinder 2.1.69 is vulnerable to a Server-Side Request Forgery (SSRF) protection bypass when PHP cURL is unavailable and URL uploads use the `fsock_get_contents()` fallback.

An attacker who can submit a URL for server-side upload can use an attacker-controlled DNS hostname that initially resolves to an allowed public IP address and subsequently resolves to a loopback or private IP address.

The URL validation checks the first resolved IP, but `fsock_get_contents()` opens the actual connection using the original hostname. This causes a second DNS resolution and allows the connection to reach an address different from the one that was validated.

The response from the internal service is saved as an uploaded file and can be read through elFinder. This makes the demonstrated issue a non-blind SSRF.

The most accurate classification is:

* Vulnerability: SSRF protection bypass 
* Exploitation technique: DNS rebinding
* Root cause: TOCTOU/double DNS resolution without IP pinning

## Affected versions

Confirmed affected:

* elFinder 2.1.69, commit `8f2c3ffafcdd52cf4515f1eec172f4eee44552ad`
* the current `master` branch inspected on 24 July 2026

The earliest affected version has not been determined.

## Preconditions

The demonstrated readback path requires:

* PHP without the cURL extension (`curl_exec()` unavailable);
* access to the URL upload functionality;
* permission to upload a MIME type returned by the target service;
* network connectivity from the PHP process to the internal target;
* DNS resolution behavior compatible with low or zero TTL responses.

Authentication requirements depend on the application integrating the elFinder connector. The attached reproduction connector is intentionally minimal and unauthenticated.

## Technical details

`validate_address()` resolves the supplied hostname with `gethostbyname()`, rejects loopback and private ranges, and stores the accepted address in `$info['ip']`:

https://github.com/Studio-42/elFinder/blob/2.1.69/php/elFinder.class.php#L2587-L2655

`get_remote_contents()` then selects cURL when available, otherwise `fsock_get_contents()`:

https://github.com/Studio-42/elFinder/blob/2.1.69/php/elFinder.class.php#L2673-L2689

The cURL implementation correctly pins the validated IP using `CURLOPT_RESOLVE`:

https://github.com/Studio-42/elFinder/blob/2.1.69/php/elFinder.class.php#L2709-L2736

However, the socket fallback ignores `$info['ip']` and connects using `$arr['host']`:

```php
$fp = fsockopen(
    $ssl . $arr['host'],
    $arr['port'],
    $errno,
    $errstr,
    $connect_timeout
);
```

Relevant code:

https://github.com/Studio-42/elFinder/blob/2.1.69/php/elFinder.class.php#L2762-L2866

Consequently, the address checked by `validate_address()` is not necessarily the address used by the socket connection.

The same problem is present after redirects: the redirect URL is validated, but the recursive socket request again connects using the hostname rather than the validated IP.

## Proof of concept

A Docker-based reproduction is attached as `poc.zip`.

The laboratory:

* downloads the official elFinder 2.1.69 release during the build;
* verifies that the package version is 2.1.69;
* verifies that `curl_exec()` is unavailable;
* does not modify the elFinder core;
* runs a deterministic DNS server and an HTTP service bound only to loopback.

Build and run:

```sh
docker build -t elfinder-ssrf-repro poc
docker run --rm -p 127.0.0.1:8081:8081 elfinder-ssrf-repro
```

Open:

```text
http://127.0.0.1:8081/poc/index.html
```

In the elFinder interface:

1. Select "Upload".
2. Paste the following URL:

```text
http://rebind.test:9001/secret.txt
```

3. Wait for the upload to complete.
4. Open the resulting `secret.txt` file.

Observed content:

```text
INTERNAL_SECRET_MANUAL
```

The PoC DNS server responds as follows:

```text
first A resolution       -> 203.0.113.10
subsequent A resolutions -> 127.0.0.1
```

Expected logs include:

```text
DNS rebind.test type=1 answer=203.0.113.10 count=1
DNS rebind.test type=1 answer=127.0.0.1 count=2
GET /secret.txt
```

`203.0.113.10` is used only as a deterministic laboratory address that passes the current private-address checks. The actual connection reaches `127.0.0.1:9001`.

A redirect variant is also included:

```text
http://rebind.test:9001/redirect-secret
```

It produces the same readable internal content.

## Security impact

An attacker may cause the elFinder server to issue HTTP GET requests to services reachable from the PHP process, including:

* loopback services;
* private network services;
* link-local services where reachable;
* internal administrative or application endpoints.

Because the response body is saved and exposed through elFinder, sensitive internal information may be disclosed.

The demonstrated primitive is limited to HTTP GET requests and does not provide arbitrary request methods, bodies, or headers. Integrity and availability impact would depend on the behavior of reachable internal endpoints and are not claimed by this PoC.

## Suggested CVSS

For an exposed connector matching the attached PoC:

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N
```

Base score: 8.6 High.

This assumes:

* no authentication is required by the connector;
* the internal service represents a separate security scope;
* disclosure may include highly sensitive internal data.

If authenticated user access is considered an inherent prerequisite, `PR:L` would result in a score of 7.7 High.

## Suggested remediation

The socket connection should use the IP address returned by `validate_address()` rather than resolving the hostname again.

For HTTPS, the original hostname should still be used for:

* the HTTP `Host` header;
* TLS SNI;
* certificate hostname validation.

This may require replacing `fsockopen()` with a connection mechanism that supports connecting to the validated IP while explicitly configuring the TLS peer name.

Every redirect destination should be independently validated and its validated IP pinned to that specific connection.

Revalidating the hostname immediately before connecting is not sufficient because it would still leave a validation-to-connection DNS resolution gap.

As a temporary mitigation, URL uploads could be rejected when cURL is unavailable, or deployments could configure `urlUploadFilter` to reject URL uploads.

## Additional observation

After a successful URL fetch, the upload path calls:

```php
get_headers($url, true)
```

Relevant code:

https://github.com/Studio-42/elFinder/blob/2.1.69/php/elFinder.class.php#L3356-L3374

This performs another request using the original hostname without reusing the validated and pinned connection. It may therefore introduce an additional blind SSRF request, potentially even when the cURL download path is selected.

This additional request is not required for the attached non-blind `fsock_get_contents()` PoC. It should nevertheless be reviewed during remediation. Ideally, filename and response-header information should be collected from the already validated HTTP response instead of issuing a separate request.

## Disclosure

Initial private report date: `24/07/2026`

Reporter contact: `Marco Lunardi - marcolunardi90@gmail.com`

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-8x3q-jpjh-qh5c
- https://github.com/Studio-42/elFinder/commit/191372c1bbebbd36fb55af79a84b9984861390ff
- https://github.com/Studio-42/elFinder/commit/6d997386cd0f1abab4706c220b46b0aea0ecff51
- https://github.com/Studio-42/elFinder
- https://github.com/Studio-42/elFinder/releases/tag/2.1.70
