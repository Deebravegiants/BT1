# [H] FTP shutdown response buffer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2018-1000300
Aliases: CVE-2018-1000300
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CURL-CVE-2018-1000300
Type: osv

## Details
curl might overflow a heap based memory buffer when closing down an FTP
connection with long server command replies.

When doing FTP transfers, curl keeps a spare "closure handle" around
internally that is used when an FTP connection gets shut down since the
original curl easy handle is then already removed.

FTP server response data that gets cached from the original transfer might
then be larger than the default buffer size (16 KB) allocated in the "closure
handle", which can lead to a buffer overwrite. The contents and size of that
overwrite is controllable by the server.

This situation was detected by an assert() in the code, but that was of course
only preventing bad stuff in debug builds. This bug is highly unlikely
to trigger with non-malicious servers.
