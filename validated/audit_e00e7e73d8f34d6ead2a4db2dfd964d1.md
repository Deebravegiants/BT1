Confirmed: `Utils::VerifiableQuery#to_signable_string` is the only material the HMAC covers, and `Webhooks::Request#to_signable_string` returns just `@raw_body`, while `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without being included in that signable string. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches the webhook to the app's handler using the `shop` value read from an unauthenticated header. Because the `shop-domain` header is never part of the signed payload, the binding "shop the HMAC authenticates" == "shop the handler acts on" does not hold, allowing a party who possesses one valid `(body, hmac)` pair to relabel it as belonging to any other shop.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it with the received `hmac` value using `OpenSSL.secure_compare`: [4](#0-3) 

For webhooks, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

The `shop` accessor, however, is parsed directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of `to_signable_string` and therefore is never checked by the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed into the app's handler: [5](#0-4) 

Because the HMAC is computed with the app's shared `api_secret_key` and does not incorporate the shop identifier, any `(body, hmac)` pair that is valid for one shop is *also* valid for every other shop on the same app — the signature check passes identically regardless of which `shop-domain` header value is attached. A single valid webhook body signature (e.g., a common body such as `{}` for topics like `shop/redact`, or any deterministic/guessable payload for a topic the attacker can trigger from their own shop) is therefore transferable across the header-declared `shop`, letting the header claim an entirely different, victim merchant's domain while still passing `HmacValidator.validate`.

This breaks the intended equality: "shop cryptographically authenticated by HMAC" == "shop acted upon by the webhook handler." The gem verifies the *bytes of the body* but *acts on the header*, which is exactly the unauthenticated-field pattern described by the M-13 analog (a field acted upon but not covered by the integrity check).

### Impact Explanation
This is a cross-tenant authentication/identity issue: an attacker who operates their own installation of the same app (a routine, unprivileged capability — installing a public/multi-tenant app on their own trial store) can obtain genuine `(body, hmac)` pairs signed with the app's `api_secret_key` for topics with deterministic or attacker-influenced bodies, then replay them with a forged `shop-domain` header naming a victim shop. Any host application that trusts `WebhookMetadata#shop` from this gem (as documented/intended usage, e.g., to select the tenant's data store, session, or DB record to update) will process the update against the wrong shop, leading to cross-tenant data corruption or disclosure — satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is constrained by two factors: (1) the attacker needs at least one genuine `(body, hmac)` pair, which is trivially obtainable if the app is multi-tenant/publicly installable (the attacker installs it on their own store and receives real webhooks with predictable bodies for many topics, e.g. mandatory GDPR topics or empty-body topics), and (2) the impact depends on the host app's handler trusting `shop` for a security-relevant decision, which is the gem's documented usage pattern (`WebhookMetadata.new(... shop: request.shop ...)`). Given these are ordinary, unprivileged capabilities of any app installer, likelihood is Medium-to-High for apps installable by third parties.

### Recommendation
Include the shop domain (and ideally the webhook topic/id) inside the signable string used for webhook HMAC verification, or otherwise cryptographically bind the `shop-domain` header value before it is trusted — e.g., have `Webhooks::Request#to_signable_string` incorporate `shop` alongside `@raw_body`, and reject the webhook if that combined signature does not validate. Alternatively, document and enforce that host apps must independently verify `shop` against their own webhook subscription records (keyed by webhook id) rather than trusting the header value outright.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app there.
# Shopify legitimately delivers a webhook with an empty body "{}" for topic "shop/redact"
# (a mandatory topic with deterministic body), signed with the app's real api_secret_key:

real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, "{}")
encoded_hmac = Base64.encode64(real_hmac)

# Attacker now replays the SAME body + SAME hmac, but swaps the shop-domain header
# to a victim shop the attacker does not control:
forged_headers = {
  "x-shopify-topic" => "shop/redact",
  "x-shopify-hmac-sha256" => encoded_hmac,          # unchanged, still valid for body "{}"
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # forged, not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)

# This succeeds: HmacValidator only checks the body, not the shop header.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "shop/redact",
#      shop: "victim-shop.myshopify.com", body: {}, ...))
# The app's handler now performs a shop/redact-style action against the victim's
# tenant, even though the victim never sent this webhook.
```

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
