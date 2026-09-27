# [M] TELNET stack contents disclosure

## Summary
Severity: Medium
Advisory: CURL-CVE-2021-22898
Aliases: CVE-2021-22898
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22898
Type: osv

## Details
curl supports the `-t` command line option, known as `CURLOPT_TELNETOPTIONS`
in libcurl. This rarely used option is used to send variable=content pairs to
TELNET servers.

Due to flaw in the option parser for sending `NEW_ENV` variables, libcurl
could be made to pass on uninitialized data from a stack based buffer to the
server. Therefore potentially revealing sensitive internal information to the
server using a clear-text network protocol.

This could happen because curl did not check the return code from a
`sscanf(command, "%127[^,],%127s")` function invoke correctly, and would leave
the piece of the send buffer uninitialized for the value part if it was
provided longer than 127 bytes. The buffer used for this is 2048 bytes big and
the *variable* part of the *variable=content* pairs would be stored correctly
in the send buffer, making curl sending "interleaved" bytes sequences of stack
contents. A single curl TELNET handshake could then be made to send off a
total of around 1800 bytes of (non-contiguous) stack contents in this style:

    [control byte]name[control byte]
    stack contents
    [control byte]name[control byte]
    stack contents
    ...

An easy proof of concept command line looks like this:

    curl telnet://example.com -tNEW_ENV=a,bbbbbb (256 'b's)
