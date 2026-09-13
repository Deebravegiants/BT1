# [H] ReDoS( Ruby, Time)

## Summary
Severity: High
Program: Internet Bug Bounty
Weakness: Uncontrolled Resource Consumption
Reporter: ooooooo_q
State: resolved
Disclosed: 2023-04-26T03:36:32.774Z
CVE: CVE-2023-28756
Source: https://hackerone.com/reports/1929567

## Details
I reported at https://hackerone.com/reports/1485501

https://www.ruby-lang.org/en/news/2023/03/30/redos-in-time-cve-2023-28756/
> The Time parser mishandles invalid strings that have specific characters. It causes an increase in execution time for parsing strings to Time objects.
> A ReDoS issue was discovered in the Time gem 0.1.0 and 0.2.1 and Time library of Ruby 2.7.7.

## Impact

ReDoS occurs when `Time.rfc2822` accepts user input.

In `Rack::ConditionalGet`, the header value is parsed by `Time.rfc2822`,  it is possible to attack from the request.
Rails uses `::Rack::ConditionalGet` by default, it can be attacked by a request from the client.
