# [M] Envoy affected by off-by-one write in JsonEscaper::escapeString()

## Summary
Severity: Medium
Advisory: GHSA-56cj-wgg3-x943
CVE: CVE-2026-26309
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-56cj-wgg3-x943
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected 1.37.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0
- Go: `github.com/envoyproxy/envoy` — affected >=0

## Details
### Summary

  An off-by-one write in Envoy::JsonEscaper::escapeString() can corrupt
  std::string null-termination, causing undefined behavior and potentially
  leading to crashes or out-of-bounds reads when the resulting string is later
  treated as a C-string.

  ### Details

  The bug is in the control-character escaping path in source/common/common/
  json_escape_string.h:67.

  - The function pre-sizes result to the final length: std::string
    result(input.size() + required_size, '\\');
  - For control characters (0x00..0x1f), it emits a JSON escape sequence of
    length 6: \u00XX.
  - It uses sprintf(&result[position + 1], "u%04x", ...), which writes 5 chars +
    a trailing NUL (\0) starting at result[position + 1].
  - Then it does position += 6; and writes result[position] = '\\'; to overwrite
    the NUL.
  - If the control character occurs at the end of the output (e.g., the input
    ends with \x01), then after position += 6, position == result.size(), so
    result[position] is one past the end (off-by-one), violating std::string
    bounds/contract.

  Concretely, the problematic lines are:

  - source/common/common/json_escape_string.h:69 (sprintf(...))
  - source/common/common/json_escape_string.h:72 (result[position] = '\\';)

  Potentially reachable from request-driven paths that escape untrusted data,
  e.g. invalid header reporting:

  - source/common/http/header_utility.cc:538 ~ source/common/http/
    header_utility.cc:546 (escapes invalid header key for error text)

  Even when this doesn’t immediately crash, it can break the std::string
  requirement that c_str()[size()] == '\0', which can later trigger UB (e.g., if
  passed to strlen, printf("%s"), or any C API that expects NUL termination).
  
  
  ```cpp
//clang++ -std=c++20 -O0 -g -fsanitize=address -fno-omit-frame-pointer
  repro_json_escape_asan.cc -o repro_json_escape_asan
  ASAN_OPTIONS=abort_on_error=1 ./repro_json_escape_asan
#include <cstdint>
  #include <cstdio>
  #include <cstring>
  #include <string>
  #include <string_view>

  static uint64_t extraSpace(std::string_view input) {
    uint64_t result = 0;
    for (unsigned char c : input) {
      switch (c) {
      case '\"':
      case '\\':
      case '\b':
      case '\f':
      case '\n':
      case '\r':
      case '\t':
        result += 1;
        break;
      default:
        if (c == 0x00 || (c > 0x00 && c <= 0x1f)) {
          result += 5;
        }
        break;
      }
    }
    return result;
  }

  static std::string escapeString(std::string_view input, uint64_t
  required_size) {
    std::string result(input.size() + required_size, '\\');
    uint64_t position = 0;

    for (unsigned char character : input) {
      switch (character) {
      case '\"':
        result[position + 1] = '\"';
        position += 2;
        break;
      case '\\':
        position += 2;
        break;
      case '\b':
        result[position + 1] = 'b';
        position += 2;
        break;
      case '\f':
        result[position + 1] = 'f';
        position += 2;
        break;
      case '\n':
        result[position + 1] = 'n';
        position += 2;
        break;
      case '\r':
        result[position + 1] = 'r';
        position += 2;
        break;
      case '\t':
        result[position + 1] = 't';
        position += 2;
        break;
      default:
        if (character == 0x00 || (character > 0x00 && character <= 0x1f)) {
          std::sprintf(&result[position + 1], "u%04x",
  static_cast<int>(character));
          position += 6;
          // Off-by-one when this escape is the last output chunk:
          // position can become result.size(), so result[position] is out of
  bounds.
          result[position] = '\\';
        } else {
          result[position++] = static_cast<char>(character);
        }
        break;
      }
    }

    return result;
  }

  int main() {
    std::string input(4096, 'A');
    input.push_back('\x01'); // ends with a control char -> triggers the buggy
  path at the end

    const uint64_t required = extraSpace(input);
    std::string escaped = escapeString(input, required);

    std::printf("escaped.size=%zu\n", escaped.size());
    unsigned char terminator = static_cast<unsigned char>(escaped.c_str()
  [escaped.size()]);
    std::printf("escaped.c_str()[escaped.size()] = 0x%02x\n", terminator);

    // If NUL termination is corrupted, this can read past the logical end.
    std::printf("strlen(escaped.c_str()) = %zu\n",
  std::strlen(escaped.c_str()));
    return 0;
  }```

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-56cj-wgg3-x943
- https://nvd.nist.gov/vuln/detail/CVE-2026-26309
- https://github.com/envoyproxy/envoy
