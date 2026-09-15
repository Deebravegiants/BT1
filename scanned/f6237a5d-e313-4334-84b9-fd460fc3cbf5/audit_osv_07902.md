# [H] NTLMv2 type-3 header stack buffer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2019-3822
Aliases: CVE-2019-3822
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CURL-CVE-2019-3822
Type: osv

## Details
libcurl contains a stack based buffer overflow vulnerability.

The function creating an outgoing NTLM type-3 header
(`lib/vauth/ntlm.c:Curl_auth_create_ntlm_type3_message()`), generates the
request HTTP header contents based on previously received data. The check that
exists to prevent the local buffer from getting overflowed is implemented
wrongly (using unsigned math) and as such it does not prevent the overflow
from happening.

This output data can grow larger than the local buffer if large response data
is extracted from a previous NTLMv2 header provided by the malicious or broken
HTTP server.

Such large response data needs to be around 1000 bytes or more. The actual
payload data copied to the target buffer comes from the NTLMv2 type-2 response
header.
