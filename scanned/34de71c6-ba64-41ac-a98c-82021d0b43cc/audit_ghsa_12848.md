# [M] XML-RPC for PHP allows access to local files via malicious argument to the Client::send method

## Summary
Severity: Medium
Advisory: GHSA-m95x-m25c-w9mp
Ecosystem: Packagist
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-m95x-m25c-w9mp
Type: github-advisory

## Affected
- Packagist: `phpxmlrpc/phpxmlrpc` — affected >=0 <4.9.0

## Details
Abusing the `$method` argument of Client::send, it was possible to force the client to _access local files_ or _connect to undesired urls_ instead of the intended target server's url (the one used in the Client constructor).

This weakness only affects installations where all the following conditions apply, at the same time:

- the xmlrpc Client is used, ie. not xmlrpc servers
- untrusted data (eg. data from remote users) is used as value for the `$method` argument of method `Client::send()`, in conjunction with conditions which trigger usage of curl as http transport (ie. either using the https, http11 or http2 protocols, or calling `Client::setUseCurl()` beforehand)
- either have set the Clients `return_type` property to 'xml', or make the resulting Response's object `httpResponse` member, which is intended to be used for debugging purposes only, available to 3rd parties, eg. by displaying it to the end user or serializing it in some storage (note that the same data can also be accessed via magic property `Response::raw_data`, and in the Request's `httpResponse` member)

This is most likely a very uncommon usage scenario, and as such the chances of exploitation of this issue may be low.

If it is not possible to upgrade to this release of the library at this time, a proactive security measure, to avoid the Client accessing any local file on the server which hosts it, is to add the following call to your code:

      $client->setCurlOptions([CURLOPT_PROTOCOLS, CURLPROTO_HTTPS|CURLPROTO_HTTP]);

Originally reported as issue #81

## References
- https://github.com/gggeek/phpxmlrpc/security/advisories/GHSA-m95x-m25c-w9mp
- https://github.com/gggeek/phpxmlrpc/issues/81
- https://github.com/gggeek/phpxmlrpc/commit/cf6e605e09d001ce520bfa8e7b168cfa514e663b
- https://github.com/gggeek/phpxmlrpc
