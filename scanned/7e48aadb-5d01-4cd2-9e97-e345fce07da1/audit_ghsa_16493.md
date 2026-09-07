# [H] Symfony allows direct access of ESI URLs behind a trusted proxy

## Summary
Severity: High
Advisory: GHSA-wvjv-p5rr-mmqm
CVE: CVE-2014-5245
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-wvjv-p5rr-mmqm
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/http-kernel` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/http-kernel` — affected >=2.5.0 <2.5.4
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/symfony` — affected >=2.5.0 <2.5.4

## Details
All 2.2.X, 2.3.X, 2.4.X, and 2.5.X versions of the Symfony HttpKernel component are affected by this security issue. Your application is vulnerable only if the ESI feature is enabled and there is a proxy in front of the web application.

This issue has been fixed in Symfony 2.3.19, 2.4.9, and 2.5.4. Note that no fixes are provided for Symfony 2.2 as it is not maintained anymore.

Description
When you enable the ESI feature and when you are using a proxy like Varnish that you configured as a trusted proxy, the `FragmentHandler` considered requests to render fragments as coming from a trusted source, even if the client was requesting them directly. Symfony can not distinguish between ESI requests done on behalf of the client by Varnish and faked fragment requests coming directly from the client.

To mitigate this issue, and for not-supported Symfony versions, you can use the following workaround in your Varnish configuration (`/_fragment` being the URL path prefix configured under the `fragment` setting of the framework bundle configuration):

 Copy
sub vcl_recv {
    if (req.restarts == 0 && req.url ~ "^/_fragment") {
        error 400;
    }
}
Resolution
We do not rely on trusted IPs anymore when validating a fragment request as all fragment URLs are now signed.

The patch for this issue is available here: https://github.com/symfony/symfony/pull/11831

## References
- https://github.com/symfony/symfony/pull/11831
- https://github.com/symfony/symfony/commit/654b1f281e09dd96ffbbd3da815411700423ecf5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2014-5245.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2014-5245.yaml
- https://symfony.com/cve-2014-5245
