# [M] ewen-lbh/ffcss Late-Unicode normalization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wpmx-564x-h2mh
CVE: CVE-2023-52081
CWE: CWE-176, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-wpmx-564x-h2mh
Type: github-advisory

## Affected
- Go: `github.com/ewen-lbh/ffcss` — affected >=0 <0.2.0

## Details
### Summary
The function `lookupPreprocess()` is meant to apply some transformations to a string by disabling characters in the regex `[-_ .]`. However, due to the use of late Unicode normalization of type NFKD, it is possible to bypass that validation and re-introduce all the characters in the regex `[-_ .]`. 

```go
// lookupPreprocess applies transformations to s so that it can be compared
// to search for something.
// For example, it is used by (ThemeStore).Lookup
func lookupPreprocess(s string) string {
	return strings.ToLower(norm.NFKD.String(regexp.MustCompile(`[-_ .]`).ReplaceAllString(s, "")))
}
``` 

Take the following equivalent Unicode character U+2024 (․). Initially, the `lookupPreprocess()` function would compile the regex and replace the regular dot (.). However, the U+2024 (․) would bypass the `ReplaceAllString()`. When the normalization operation is applied to U+2024 (․), the resulting character will be U+002E (.). Thus, the dot was reintroduced back.

### Impact

The `lookupPreprocess()` can be easily bypassed with equivalent Unicode characters like U+FE4D (﹍), which would result in the omitted U+005F (_), for instance. It should be noted here that the variable `s` is user-controlled data coming from [/cmd/ffcss/commands.go#L22-L28](https://github.com/ewen-lbh/ffcss/blob/master/cmd/ffcss/commands.go#L22-L28) the command args. The `lookupPreprocess()` function is only ever used to search for themes loosely (case insensitively, while ignoring dashes, underscores and dots), so the actual security impact is classified as low.

### Remediation

A simple fix would be to initially perform the Unicode normalization and then the rest of validations.

### References

 - https://sim4n6.beehiiv.com/p/unicode-characters-bypass-security-checks

## References
- https://github.com/ewen-lbh/ffcss/security/advisories/GHSA-wpmx-564x-h2mh
- https://nvd.nist.gov/vuln/detail/CVE-2023-52081
- https://github.com/ewen-lbh/ffcss/commit/f9c491874b858a32fcae15045f169fd7d02f90dc
- https://github.com/ewen-lbh/ffcss
