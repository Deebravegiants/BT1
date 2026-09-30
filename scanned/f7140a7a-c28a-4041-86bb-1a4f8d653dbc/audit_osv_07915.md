# [M] OAUTH2 bearer bypass in connection reuse

## Summary
Severity: Medium
Advisory: CURL-CVE-2022-22576
Aliases: CVE-2022-22576
Published: 2022-04-27
Source: https://osv.dev/vulnerability/CURL-CVE-2022-22576
Type: osv

## Details
libcurl might reuse OAUTH2-authenticated connections without properly making
sure that the connection was authenticated with the same credentials as set
for this transfer. This affects SASL-enabled protocols: SMTP(S), IMAP(S),
POP3(S) and LDAP(S) (OpenLDAP only).

libcurl maintains a pool of live connections after a transfer has completed
(sometimes called the connection cache). This pool of connections is then gone
through when a new transfer is requested and if there is a live connection
available that can be reused, it is preferred instead of creating a new one.

Due to this security vulnerability, a connection that is successfully created
and authenticated with a username + OAUTH2 bearer could subsequently be
erroneously reused even for user + [other OAUTH2 bearer], even though that
might not even be a valid bearer. This could lead to an authentication bypass,
either by mistake or by a malicious actor.
