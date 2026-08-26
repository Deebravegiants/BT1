# [M] ReDoS in net/http affects webhooks: Sidekiq job stuck at 100% CPU for a year

## Summary
Severity: Medium (CVSS 4.3)
Program: GitLab
Weakness: Uncontrolled Resource Consumption
Reporter: afewgoats
State: resolved
Disclosed: 2022-09-13T04:42:18.678Z
Source: https://hackerone.com/reports/1531958

## Details
### Summary

A Gitlab webhook may be pointed at a malicious webhook receiver.
The webhook receiver can respond with a specially crafted long header.
Gitlab processes the header with Ruby's net/http where there is a regular expression operation with quadratic complexity (ReDoS).
This causes the `web_hook` Sidekiq job to get stuck at 100% CPU utilisation until the regular expression processing is complete (weeks later).
The long headers are also kept in memory and the connection can be kept open.

#### Comparison to 1252116

In report #1252116, the impact was that the network connection was kept open indefinitely, potentially causing connection pool and memory exhaustion. This new report is instead about CPU exhaustion for a more serious and more powerful DoS. It also bypasses the timeout added to fix #1252116 (https://gitlab.com/gitlab-org/gitlab/-/commit/a8807ee52d0b22b68beb31f0cad6ad5b77b4caf6) (deployed in 14.9.2) as the timeout only gets hit once the regular expression has finished processing (timeout is checked between header lines).

#### The root cause

A Regular Expression Denial of Service (ReDoS) vulnerability in Ruby's net/http affects Gitlab webhooks.

The bug is in [net/http/response.rb#57](https://github.com/ruby/net-http/blob/7b852b1feb7c1c0bc3019687d6ee5c385ce26eb9/lib/net/http/response.rb#L57) when reading headers line by line:

```rb
line = sock.readuntil("\n", true).sub(/\s+\z/, '')
```

The `sub` regex is the issue. While it looks safe and linear, the `sub` operation will actually have quadratic complexity as there is no starting anchor.

A header line which contains many consecutive spaces but *does not end in a space*, such as

```rb
( "a" + " " * 950000 + "b" ).sub(/\s+\z/, '')
```

will exhibit extreme backtracking.

The time complexity is quadratic with respect to the number of spaces in the string (doubling the number of spaces quadruples the processing time). Approximate timings from my laptop (I measured until 10,000 and then extrapolated):

```
|  Spaces  |  Seconds   |  Hours   |  Days  |
|----------|------------|----------|--------|
|     2000 |        1.8 |          |        |
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1531958_
