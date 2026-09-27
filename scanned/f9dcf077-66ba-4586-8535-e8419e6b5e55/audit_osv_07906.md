# [M] curl overwrite local file with -J

## Summary
Severity: Medium
Advisory: CURL-CVE-2020-8177
Aliases: CVE-2020-8177
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CURL-CVE-2020-8177
Type: osv

## Details
curl can be tricked by a malicious server to overwrite a local file when using
`-J` (`--remote-header-name`) and `-i` (`--include`) in the same command line.

The command line tool offers the `-J` option that saves a remote file using
the filename present in the `Content-Disposition:` response header. curl then
refuses to overwrite an existing local file using the same name, if one
already exists in the current directory.

The `-J` flag is designed to save a response body, and so it does not work
together with `-i` and there is logic that forbids it. However, the check is
flawed and does not properly check for when the options are used in the
reversed order: first using `-J` and then `-i` were mistakenly accepted.

The result of this mistake was that incoming HTTP headers could overwrite a
local file if one existed, as the check to avoid the local file was done first
when body data was received, and due to the mistake mentioned above, it could
already have received and saved headers by that time.

The saved file would only get response headers added to it, as it would abort
the saving when the first body byte arrives. A malicious server could however
still be made to send back virtually anything as headers and curl would save
them like this, until the first CRLF-CRLF sequence appears.

(Also note that `-J` needs to be used in combination with `-O` to have any
effect.)
