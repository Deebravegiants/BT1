# [M] CVE-2023-28755: ReDoS vulnerability in URI

## Summary
Severity: Medium (CVSS 6.5)
Program: Internet Bug Bounty
Weakness: Uncontrolled Resource Consumption
Reporter: dee-see
State: resolved
Disclosed: 2023-04-26T16:34:34.061Z
CVE: CVE-2023-28755
Source: https://hackerone.com/reports/1944515

## Details
Original report on the Ruby program: https://hackerone.com/reports/1444501
Advisort: https://www.ruby-lang.org/en/news/2023/03/28/redos-in-uri-cve-2023-28755/
NIST entry: https://nvd.nist.gov/vuln/detail/CVE-2023-28755
CVSS:  7.5 high `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` as listed by NIST but frankly I disagree with the `UI:N` part, I won't mind the extra 2k if you go with NIST but it didn't feel right not to mention it :) I filed the report with the CVSS I think this should have

Copy of the original report:

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


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1944515_
