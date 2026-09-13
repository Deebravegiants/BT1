# [M] Potential access to sensitive URLs via CKAN extensions (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-g9ph-j5vj-f8wm
CVE: CVE-2024-43371
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-g9ph-j5vj-f8wm
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=0 <2.10.5

## Details
### Impact

There are a number of CKAN plugins, including [XLoader](https://github.com/ckan/ckanext-xloader), [DataPusher](https://github.com/ckan/datapusher), [Resource proxy](https://docs.ckan.org/en/latest/maintaining/data-viewer.html#resource-proxy) and [ckanext-archiver](https://github.com/ckan/ckanext-archiver/), that work by downloading the contents of local or remote files in order to perform some actions with their contents (e.g. pushing to the DataStore, streaming contents or saving a local copy). All of them use the resource URL, and there are currently no checks to limit what URLs can be requested. This means that a malicious (or unaware) user can create a resource with a URL pointing to a place where they should not have access in order for one of the previous tools to retrieve it (known as a [Server Side Request Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)).

### Patches and Workarounds

Users wanting to protect against these kinds of attacks can use one or a combination of the following approaches:

* Use a separate HTTP proxy like [Squid](https://www.squid-cache.org/) that can be used to allow / disallow IPs, domains etc as needed, and make CKAN extensions aware of this setting via the [`ckan.download_proxy`](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-download-proxy) config option. 
* Implement custom firewall rules to prevent access to restricted resources.
* Use custom validators on the resource `url` field to block/allow certain domains or IPs.

All latest versions of the plugins linked above support the `ckan.download_proxy` settings. Support for this setting in the Resource Proxy plugin was included in CKAN 2.10.5 and 2.11.0

### References

* [Blog post](https://feeding.cloud.geek.nz/posts/restricting-outgoing-webapp-requests-using-squid-proxy/) provides more details on how to configure a Squid proxy to prevent these issues

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-g9ph-j5vj-f8wm
- https://nvd.nist.gov/vuln/detail/CVE-2024-43371
- https://github.com/ckan/ckan/commit/382beaec98cb331f2a030459ef043c50eaf5ad53
- https://github.com/ckan/ckan/commit/8601183cc2fc87277ea5b33ff75c3a5610812ab5
- https://github.com/ckan/ckan
