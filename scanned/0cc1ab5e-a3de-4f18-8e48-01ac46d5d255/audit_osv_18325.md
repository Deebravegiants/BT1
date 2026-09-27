# [C] CVE-2020-26168

## Summary
Severity: Critical
Advisory: CVE-2020-26168
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-09
Source: https://osv.dev/vulnerability/CVE-2020-26168
Type: osv

## Details
The LDAP authentication method in LdapLoginModule in Hazelcast IMDG Enterprise 4.x before 4.0.3, and Jet Enterprise 4.x through 4.2, doesn't verify properly the password in some system-user-dn scenarios. As a result, users (clients/members) can be authenticated even if they provide invalid passwords.

## References
- https://docs.hazelcast.org/docs/ern/index.html#4-0-3
- https://hazelcast.zendesk.com/hc/en-us/articles/360050161951--IMDG-Enterprise-4-0-4-0-1-4-0-2-LDAP-Authentication-Bypass
- https://hazelcast.zendesk.com/hc/en-us/articles/360051384932--JET-Enterprise-4-0-4-1-4-1-1-4-2-LDAP-Authentication-Bypass
- https://jet-start.sh/blog/2020/10/23/jet-43-is-released
