# [H] mezzio-swoole Applications Using Diactoros Vulnerable to HTTP Host Header Attack

## Summary
Severity: High
Advisory: GHSA-c8rp-cgf4-937w
Ecosystem: Packagist
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-c8rp-cgf4-937w
Type: github-advisory

## Affected
- Packagist: `mezzio/mezzio-swoole` — affected >=0 <3.7.0
- Packagist: `mezzio/mezzio-swoole` — affected >=4.0.0 <4.3.0

## Details
### Impact

mezzio-swoole applications using Diactoros for their PSR-7 implementation, and which are either not behind a proxy, or can be accessed via untrusted proxies, can potentially have the host, protocol, and/or port of a `Laminas\Diactoros\Uri` instance associated with the incoming server request modified to reflect values from `X-Forwarded-*` headers. Such changes can potentially lead to XSS attacks (if a fully-qualified URL is used in links) and/or URL poisoning.

### Patches

3.7.0, and 4.3.0 and later.

The patches present in these versions update the `SwooleServerRequestFactory` to filter out `X-Forwarded-*` headers when creating the initial request. They then by default pass that instance through a `Laminas\Diactoros\ServerRequestFilter\FilterUsingXForwardedHeaders` instance created from the `trustReservedSubnet()` constructor, ensuring that the request only honors the `X-Forwarded-*` headers for private reserved subnets.

Users can define the `Laminas\Diactoros\ServerRequestFilter\FilterServerRequestInterface` service if they wish to provide a different implementation, or configure the `FilterUsingXForwardedHeaders` instance differently. When defined, that instance will be used to filter the generated request instance.

### Workarounds

Infrastructure or DevOps can place a trusted reverse proxy in front of the mezzio-swoole server.

### References

- [HTTP Host Header Attacks](https://portswigger.net/web-security/host-header)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [mezzio/mezzio-swoole](https://github.com/mezzio/mezzio-swoole/)
- [Email us](mailto:security@getlaminas.org)

## References
- https://github.com/mezzio/mezzio-swoole/security/advisories/GHSA-c8rp-cgf4-937w
- https://github.com/mezzio/mezzio-swoole
