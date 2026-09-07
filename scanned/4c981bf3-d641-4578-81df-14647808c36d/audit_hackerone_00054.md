# [M] CVE-2024-2398: HTTP/2 push headers memory-leak

## Summary
Severity: Medium
Program: curl
Weakness: Uncontrolled Resource Consumption
Reporter: w0x42
State: resolved
Disclosed: 2024-03-27T10:33:14.061Z
CVE: CVE-2024-2398
Source: https://hackerone.com/reports/2402845

## Details
## Summary:
For each incoming `PUSH_PROMISE` header a new `name:value` string is allocated 
and the pointer to that string is stored in the `stream->push_headers` array.

```
h = aprintf("%s:%s", name, value);
    if(h)
      stream->push_headers[stream->push_headers_used++] = h;
```

Libcurl will reject `PUSH_PROMISE` frames with too many headers.
When the number of headers exceeds some threshold, `on_header` returns an error.
However, libcurl forgets to free the `stream->push_headers` array elements before `stream->push_headers` is freed.
A malicious server may continuously send `PUSH_PROMISE` frames with over 1000 headers, which would eventually consume all available memory.

The same issue exists when `Curl_saferealloc` fails.

```
 if(stream->push_headers_alloc > 1000) {
        /* this is beyond crazy many headers, bail out */
        failf(data_s, "Too many PUSH_PROMISE headers");
        Curl_safefree(stream->push_headers);
        return NGHTTP2_ERR_TEMPORAL_CALLBACK_FAILURE;
      }
      stream->push_headers_alloc *= 2;
      headp = Curl_saferealloc(stream->push_headers,
                               stream->push_headers_alloc * sizeof(char *));
      if(!headp) {
        stream->push_headers = NULL;
        return NGHTTP2_ERR_TEMPORAL_CALLBACK_FAILURE;
      }
```


## Steps To Reproduce:

  1. compile `nghttp2` with {F3099659} applied
  1. compile {F3099658}

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2402845_
