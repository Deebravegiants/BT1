# [H] ExternalName Services can be used to gain access to Envoy's admin interface

## Summary
Severity: High
Advisory: GHSA-5ph6-qq5x-7jwc
CVE: CVE-2021-32783
CWE: CWE-610
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-5ph6-qq5x-7jwc
Type: github-advisory

## Affected
- Go: `github.com/projectcontour/contour` — affected >=0 <1.14.2
- Go: `github.com/projectcontour/contour` — affected >=1.15.0 <1.15.2
- Go: `github.com/projectcontour/contour` — affected >=1.16.0 <1.16.1
- Go: `github.com/projectcontour/contour` — affected >=1.17.0 <1.17.1

## Details
### Impact
Josh Ferrell (@josh-ferrell) from VMware has reported that a specially crafted ExternalName type Service may be used to access Envoy's admin interface, which Contour normally prevents from access outside the Envoy container. This can be used to shut down Envoy remotely (a denial of service), or to expose the existence of any Secret that Envoy is using for its configuration, including most notably TLS Keypairs. However, it *cannot* be used to get the *content* of those secrets.

Since this attack allows access to the administration interface, a variety of administration options are available, such as shutting down the Envoy or draining traffic. In general, the Envoy admin interface cannot easily be used for making changes to the cluster, in-flight requests, or backend services, but it could be used to shut down or drain Envoy, change traffic routing, or to retrieve secret metadata, as mentioned above.

### Patches
The issue will be addressed in the forthcoming Contour v1.18.0 and a patch release, v1.17.1, has been released in the meantime.

It is addressed in two ways:
- disabling ExternalName type Services by default
- When ExternalName Services are enabled, block obvious "localhost" entries.

#### Disable ExternalName type Services by default

This change prohibits processing of ExternalName services unless the cluster operator specifically allows them using the new `--enable-externalname` flag or equivalent configuration file setting. This is a breaking change for previous versions of Contour, which is unfortunate, but necessary because of the severity of the information exposed in this advisory.


#### Block obvious `localhost` entries for enabled ExternalName Services

As part of this change set, we have added a filter in the event that operators *do* enable ExternalName Services, such that obvious `localhost` entries are rejected by Contour.

There are a number of problems with this method, however:
- This is a porous control. As long as you control a domain name, it's trivially easy to add a DNS entry for any name you like that redirects to `127.0.0.1` or `::1`. Contour even provides `local.projectcontour.io` ourselves for testing and example purposes. (This name is, of course, included in the "obvious localhost entries" list.) So we can never totally stop this exploit as long as the admin interface is accessible on localhost, which, according to envoyproxy/envoy#2763, will be for some time if not forever. The best we can do is block some obvious elements, but this is always a risk for a motivated attacker.
- We've actually suggested using `localhost` ExternalName Services in the past, to allow people to connect to sidecar External Authentication services in their cluster. Both of these changes break this use-case, but given that it's about something that has security requirements high enough to require authentication, it's important to ensure that people are opting in. For the External Auth sidecar case, we are investigating an update to ExtensionService that will help with the sidecar use case.

### Workarounds
Not easily. It's not possible to control the creation of ExternalName Services with RBAC without the use of Gatekeeper or other form of admission control, and the creation of services is required for Contour to actually work for application developer personas.

### For more information
Exploit code will be published at a later date for this vulnerability, once our users have had a chance to upgrade.

## References
- https://github.com/projectcontour/contour/security/advisories/GHSA-5ph6-qq5x-7jwc
- https://nvd.nist.gov/vuln/detail/CVE-2021-32783
- https://github.com/projectcontour/contour/commit/5f3e6d0ab1d48e64bae46400c85c490b200393a3
- https://github.com/projectcontour/contour/commit/b53a5c4fd927f4ea2c6cf02f1359d8e28bef852e
- https://github.com/projectcontour/contour/releases/tag/v1.14.2
- https://github.com/projectcontour/contour/releases/tag/v1.15.2
- https://github.com/projectcontour/contour/releases/tag/v1.16.1
- https://github.com/projectcontour/contour/releases/tag/v1.17.1
