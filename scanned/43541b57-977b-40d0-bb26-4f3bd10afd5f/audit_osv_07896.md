# [H] SMTP send heap buffer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2018-0500
Aliases: CVE-2018-0500
Published: 2018-07-11
Source: https://osv.dev/vulnerability/CURL-CVE-2018-0500
Type: osv

## Details
curl might overflow a heap based memory buffer when sending data over SMTP and
using a reduced read buffer.

When sending data over SMTP, curl allocates a separate "scratch area" on the
heap to be able to escape the uploaded data properly if the uploaded data
contains data that requires it.

The size of this temporary scratch area was mistakenly made to be `2 *
sizeof(download_buffer)` when it should have been made `2 *
sizeof(upload_buffer)`.

The upload and the download buffer sizes are identically sized by default
(16KB) but since version 7.54.1, curl can resize the download buffer into a
smaller buffer (as well as larger). If the download buffer size is set to a
value smaller than 10923, the `Curl_smtp_escape_eob()` function might overflow
the scratch buffer when sending contents of sufficient size and contents.

The curl command line tool lowers the buffer size when `--limit-rate` is set
to a value smaller than 16KB.
