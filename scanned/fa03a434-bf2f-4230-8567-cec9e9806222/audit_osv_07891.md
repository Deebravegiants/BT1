# [M] --write-out out of buffer read

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-7407
Aliases: CVE-2017-7407
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CURL-CVE-2017-7407
Type: osv

## Details
There were two bugs in curl's parser for the command line option `--write-out`
(or `-w` for short) that would skip the end of string zero byte if the string
ended in a `%` (percent) or `\` (backslash), and it would read beyond that
buffer in the heap memory and it could then potentially output pieces of that
memory to the terminal or the target file etc.

The curl security team did not report this as a security vulnerability due to
the minimal risk: the memory this would output comes from the process the user
itself invokes and that runs with the same privileges as the user. We could
not come up with a likely scenario where this could leak other users' data or
memory contents.

An external party registered this as a CVE with MITRE and we feel a
responsibility to clarify what this flaw is about. The CVE-2017-7407 issue is
specifically only about the `%` part of this flaw.

This flaw only exists in the command line tool.
