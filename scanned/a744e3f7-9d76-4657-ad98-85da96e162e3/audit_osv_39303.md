# [M] OpenSIPS: Denial of service in presence.handle_publish() from unchecked Content-Type state

## Summary
Severity: Medium
Advisory: CVE-2026-45084
Aliases: GHSA-h3ww-hchh-x2g9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45084
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Versions 3.4.0 through 3.6.5 contain a denial of service vulnerability in the presence module. When the presence module's handle_publish() function processes a SIP PUBLISH request with an Event: presence header and a message body while the configuration option enable_sphere_check=1 is set, it invokes the get_content_type() macro without first calling parse_content_type_hdr(), causing it to dereference uninitialized or NULL Content-Type parsing state and crash. If a Content-Type header is present but unparsed, msg->content_type->parsed is NULL and is dereferenced as a content_t pointer; if the request lacks a Content-Type header entirely, msg->content_type itself is NULL, and both cases lead to a crash. A remote attacker can therefore cause a denial of service against an affected instance with a single PUBLISH request over UDP or TCP, using either a valid Content-Type: application/pidf+xml request or one with the header removed, and the vulnerable code path itself does not enforce authentication (though a deployment's routing configuration may require it before this route is reached). The issue has been fixed in version 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45084.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-h3ww-hchh-x2g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45084
