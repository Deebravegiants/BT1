# [M] Buffer overflow in HTTP parse_hostinfo(), parse_userinfo() and parse_scheme()

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Memory Corruption - Generic
Reporter: rc0r
State: resolved
Disclosed: 2017-05-30T15:13:49.305Z
CVE: CVE-2016-7961
Source: https://hackerone.com/reports/174069

## Details
Since the original report is still marked as private in the PHP bug tracker please find the copy & pasted bug report below (edited for readability and to include correct bug tracker id). See the references section for a link to the issue in the PHP bug tracker!

The maintainer already fixed the issue in the public git repo using the proposed patch included in the original report. Fixed versions 3.1.0RC1 and 2.6.0RC1 of the pecl-http extension have been released as well.

Mitre assigned **CVE-2016-7961** for this issue.

# Description

The parsing functions of the PECL HTTP extension allow overflowing a buffer with data originating from an arbitrary HTTP request. Affected are the `parse_hostinfo()`, `parse_userinfo()` and `parse_scheme()` functions in `php_http_url.c` that may get called when instantiating/initializing an HTTP message object. The problem occurs because in the main processing loop `char *ptr` may get incremented past the corresponding end pointer `char *end` used as the end marker. Thus the parser loop may continue to execute and buffer `state->buffer` may overflow.  

Relevant code snippet from `php_http_url.c:1096`:

```c
static ZEND_RESULT_CODE parse_hostinfo(struct parse_state *state, const char *ptr)
{
[...]
    if (ptr != end) do {
        switch (*ptr) {
            [...]
            case '0': case '1': case '2': case '3': case '4': case '5': case '6':
            case '7': case '8': case '9':
                /* allowed */
                if (port) {
                    state->url.port *= 10;
                    state->url.port += *ptr - '0';
                } else {
                    label = ptr;
                    state->buffer[state->offset++] = *ptr;
                }
                break;
            [...]
            default:
            [...]
                } else if (!(mb = parse_mb(state, PARSE_HOSTINFO, ptr, end, tmp, state->flags & PHP_HTTP_URL_SILENT_ERRORS))) {
                    if (!(state->flags & PHP_HTTP_URL_IGNORE_ERRORS)) {
                        return FAILURE;
                    }
                    break;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/174069_
