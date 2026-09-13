# [H] URL decode buffer boundary flaw

## Summary
Severity: High
Advisory: CURL-CVE-2013-2174
Aliases: CVE-2013-2174
Published: 2013-06-22
Source: https://osv.dev/vulnerability/CURL-CVE-2013-2174
Type: osv

## Details
libcurl is vulnerable to a case of bad checking of the input data which may
  lead to heap corruption.

  The function curl_easy_unescape() decodes URL encoded strings to raw binary
  data. URL encoded octets are represented with %HH combinations where HH is a
  two-digit hexadecimal number. The decoded string is written to an allocated
  memory area that the function returns to the caller.

  The function takes a source string and a length parameter, and if the length
  provided is 0 the function instead uses strlen() to figure out how much data
  to parse.

  The "%HH" parser wrongly only considered the case where a zero byte would
  terminate the input. If a length-limited buffer was passed in which ended
  with a '%' character which was followed by two hexadecimal digits outside of
  the buffer libcurl was allowed to parse alas without a terminating zero,
  libcurl would still parse that sequence as well. The counter for remaining
  data to handle would then be decreased too much and wrap to become
  a large integer and the copying would go on too long and the destination
  buffer that is allocated on the heap would get overwritten.

  We consider it unlikely that programs allow user-provided strings unfiltered
  into this function. Also, only the not zero-terminated input string use case
  is affected by this flaw. Exploiting this flaw for gain is probably possible
  for specific circumstances but we consider the general risk for this to be
  low.

  The curl command line tool is not affected by this problem as it does not
  use this function.
