# [H] CVE-2026-82958

## Summary
Severity: High
Advisory: CVE-2026-82958
Aliases: GHSA-cgfq-3fv9-5c44
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-82958
Type: osv

## Details
In Eclipse Ditto versions [1.3.0, 3.9.6], the ImplicitThingCreationMessageMapper of the connectivity service builds a CreateThing command by substituting placeholder values (e.g. {{ header:device_id }}) resolved from inbound message headers into a pre-configured JSON "thing" template as raw, un-escaped strings, and then parses the resulting string as JSON. Because the placeholder engine performs no JSON escaping and is unaware of the surrounding JSON string context, a resolved value containing a double-quote character can break out of its string and inject additional JSON structure.




When a connection is configured to use this mapper with a template that reflects a header whose value a publishing device can control (for example an MQTT 5 user property, an AMQP 1.0 application property, or a Kafka record header), an attacker able to publish on that connection can inject an inline _policy object. The inline policy overrides the administrator-configured policyId, letting the attacker assign an arbitrary access-control policy to the newly created digital twin — gaining full read/write access to it and potentially revoking the legitimate owner's access, with no administrator interaction.




Exploitation requires all of the following: the connection uses the (non-default) ImplicitThingCreation mapper; its template reflects an attacker-controllable header; and, for the policy-override impact, the connection's authorization subjects are permitted to create policies (the default). Deployments that restrict the connection's subjects to thing creation only via the entity-creation configuration are not affected by the policy-override impact.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/764
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82958.json
- https://github.com/eclipse-ditto/ditto/security/advisories/GHSA-cgfq-3fv9-5c44
- https://nvd.nist.gov/vuln/detail/CVE-2026-82958
