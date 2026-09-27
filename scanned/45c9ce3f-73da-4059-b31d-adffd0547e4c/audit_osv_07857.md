# [M] Arbitrary File Access

## Summary
Severity: Medium
Advisory: CURL-CVE-2009-0037
Aliases: CVE-2009-0037
Published: 2009-03-03
Source: https://osv.dev/vulnerability/CURL-CVE-2009-0037
Type: osv

## Details
When told to follow a "redirect" automatically, libcurl does not question the
new target URL but follows it to any new URL that it understands. As libcurl
supports FILE:// URLs, a rogue server can thus "trick" a libcurl-using
application to read a local file instead of the remote one.

This is a problem, for example, when the application is running on a server
and is written to upload or to otherwise provide the transferred data to a
user, to another server or to another application etc, as it can be used to
expose local files it was not meant to.

The problem can also be exploited for uploading, if the rogue server
redirects the client to a local file and thus it would (over)write a local
file instead of sending it to the server.

libcurl compiled to support SCP can get tricked to get a file using embedded
semicolons, which can lead to execution of commands on the given
server. `Location: scp://name:passwd@host/a;date >/tmp/test;`.

Files on servers other than the one running libcurl are also accessible when
credentials for those servers are stored in the .netrc file of the user
running libcurl. This is most common for FTP servers, but can occur with
any protocol supported by libcurl. Files on remote SSH servers are also
accessible when the user has an unencrypted SSH key.
