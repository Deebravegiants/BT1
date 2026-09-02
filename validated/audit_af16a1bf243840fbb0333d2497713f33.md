### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that the host application uses to route and process an inbound webhook directly from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. The `shop` value is therefore never part of the signed material, breaking the binding "shop authenticated == shop the app acts on."

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, which requires `hmac` and `to_signable_string`: [1](#0-0) 

Its `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop` (the tenant identifier apps use to look up the correct session/access token to process the webhook) is read straight from a header, not from the signed body: [3](#0-2) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header value: [4](#0-3) 

So the equality the gem should guarantee is:
`shop-domain header authenticated by HMAC == shop used by the app to process the webhook`

but what it actually guarantees is:
`raw body authenticated by HMAC != shop-domain header used by the app`

Since Shopify's HMAC (`X-Shopify-Hmac-Sha256`) is computed only from the request body on Shopify's side too, this is not merely an implementation slip that could be trivially fixed by including more fields — it reflects that this gem's `Request#shop` accessor exposes a value with no cryptographic binding to the signature it validates, even though `HmacValidator.validate(request)` returning `true` is exactly the signal host applications use to trust `request.shop`.

### Impact Explanation
An attacker who operates their own Shopify store (unprivileged relative to any other tenant) receives legitimate webhooks for their own shop, each with a valid `X-Shopify-Hmac-Sha256` computed from the body. Because the header carrying the tenant identity (`X-Shopify-Shop-Domain`) is not part of that signed body, the attacker can take a captured, validly-signed body/HMAC pair from their own shop and resend it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `HmacValidator.validate` still returns `true` (it never inspects `shop`), and `request.shop` now returns the attacker-chosen victim domain. Any host application that trusts `ShopifyAPI::Webhooks::Request#shop` after a successful `HmacValidator.validate` — the exact usage pattern this gem exposes — will process attacker-controlled webhook data under a different merchant's tenant context, i.e., cross-tenant data injection/confusion using another shop's session/access token to act on the forged event.

### Likelihood Explanation
The webhook endpoint is, by design, a public, unauthenticated HTTP endpoint that must accept POSTs claiming to be from Shopify, and the only gem-provided defense is `HmacValidator.validate`. Obtaining a valid, replayable body+HMAC pair requires nothing more than being a legitimate merchant of the app (a very low bar — any developer can install the app on a dev/test store), and the header substitution requires no cryptographic material at all.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the material signed/verified for webhooks, or otherwise cryptographically bind the shop-domain header to the payload before `Request#shop` is trusted by callers — e.g., only accept `shop-domain` values that were established via a prior authenticated session/webhook registration for that topic, or require the host application to cross-check `request.shop` against an independently-verified registered webhook subscription rather than trusting the header value merely because `HmacValidator.validate` (which never inspects it) succeeded.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook, capturing:
raw_body = '{"id":123,"order_number":1}'
valid_hmac_from_shopify = "<hmac Shopify computed over raw_body with the app's client_secret>"

# 2. Attacker replays the exact same body + hmac to the app's public
#    webhook endpoint, only changing the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_from_shopify, # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

ShopifyAPI::Utils::HmacValidator.validate(request) # => true, because signature only covers raw_body
request.shop # => "victim-shop.myshopify.com"  (attacker-controlled, unauthenticated)

# The host app now believes this is a genuine, HMAC-verified webhook
# for "victim-shop.myshopify.com" and processes attacker-controlled
# order data / triggers side effects under the victim tenant's context.
```

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
