### Title
Unsigned `x-shopify-shop-domain` / `x-shopify-topic` headers are trusted for tenant routing after only-body HMAC validation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#topic` and `#shop` read the `shopify-topic`/`x-shopify-topic` and `shopify-shop-domain`/`x-shopify-shop-domain` headers directly, while `HmacValidator.validate` only ever authenticates `@raw_body` via `to_signable_string`. Because the signature never covers these headers, any request carrying a previously-valid `(raw_body, hmac)` pair passes validation regardless of what shop or topic is claimed, letting an attacker relabel a genuine webhook delivery as belonging to a victim shop/topic.

### Finding Description
The binding the code implicitly assumes is: `hmac == HMAC(secret, headers.topic + headers.shop + raw_body)`. In reality the code only enforces `hmac == HMAC(secret, raw_body)`: [1](#0-0) [2](#0-1) 

`topic` and `shop` are read from unsigned headers with no relation to the signed bytes: [3](#0-2) 

`Registry.process` trusts these unauthenticated values for both handler dispatch and tenant attribution once the body-only HMAC passes: [4](#0-3) 

**Exploit flow**: an attacker installs the target app on their own development shop and registers a webhook (e.g. `orders/create`). Shopify delivers a legitimately signed request to the app's public callback URL: `raw_body_A` + a valid `hmac = HMAC(api_secret_key, raw_body_A)`. The `api_secret_key` is per-app, not per-shop, so this signature is valid for the app regardless of which shop generated the body. The attacker then sends their own direct HTTP POST to the same app endpoint, re-using the exact same `raw_body_A` and `hmac`, but overriding `x-shopify-shop-domain: victim-shop.myshopify.com` and, if desired, `x-shopify-topic`. `HmacValidator.validate` recomputes `compute_signature(raw_body_A, secret)` — identical bytes, so it matches — and `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: <attacker-chosen>, shop: "victim-shop.myshopify.com", body: parsed(raw_body_A), ...)`. The handler now believes attacker-controlled body content originated from and applies to the victim tenant.

No nonce, timestamp, or webhook-id replay tracking exists in this code path, so the same `(raw_body, hmac)` pair can be replayed indefinitely against arbitrary victim shop labels. `ShopValidator` (used elsewhere in OAuth flows) is never invoked here, and no cross-check exists between the header-supplied `shop`/`topic` and the actual JSON body content.

### Impact Explanation
An unprivileged attacker who can install the target app on their own shop and trigger normal store events can forge the shop and topic attribution of any subsequently-replayed genuine payload, causing the app to process attacker-supplied data as if it belonged to an arbitrary victim merchant. Depending on the handler's trust in `WebhookMetadata#shop`/`#topic` (which this gem explicitly hands to app code as authenticated tenant context), this can result in cross-tenant data creation/mutation, or misrouting to sensitive mandatory-topic handlers (`customers/data_request`, `customers/redact`, `shop/redact`) under a victim's identity — matching the Critical cross-tenant access class.

### Likelihood Explanation
Requires only: (1) the attacker can install the app on their own development shop (explicitly permitted "unprivileged" capability), (2) the app's webhook endpoint is reachable directly over HTTP (typical for public webhook callback URLs), and (3) the app trusts `WebhookMetadata#shop`/`#topic` from `Registry.process` for tenant-scoped logic, which is the gem's documented usage pattern. No secrets are needed; the attacker only replays a signature they legitimately received for their own shop. This is cheap, deterministic, and repeatable against any victim shop domain string.

### Recommendation
Bind the routing/tenant headers into the authenticated signable string (or otherwise cryptographically tie `topic`/`shop` to the signature), and/or have `Registry.process` cross-validate `request.shop` against the caller's registered webhook subscription/URL rather than trusting the header value, and reject reused `webhook_id`/timestamp combinations to bound replay.

### Proof of Concept
Minitest sketch (WebMock/Mocha, no live shop):
```ruby
def test_replayed_body_with_relabelled_shop_and_topic_still_validates
  raw_body = '{"id":1,"note":"attacker-owned order"}'
  secret = ShopifyAPI::Context.api_secret_key
  hmac_b64 = Base64.encode64(
    OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
  )

  original = ShopifyAPI::Webhooks::Request.new(
    raw_body: raw_body,
    headers: {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => hmac_b64,
      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
    },
  )
  forged = ShopifyAPI::Webhooks::Request.new(
    raw_body: raw_body, # identical bytes -> compute_signature identical
    headers: {
      "x-shopify-topic" => "customers/data_request",
      "x-shopify-hmac-sha256" => hmac_b64,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com",
    },
  )

  assert_equal(original.hmac, forged.hmac)
  assert(ShopifyAPI::Utils::HmacValidator.validate(original))
  assert(ShopifyAPI::Utils::HmacValidator.validate(forged)) # passes despite relabelled shop/topic
  assert_equal("victim-shop.myshopify.com", forged.shop)
  assert_equal("customers/data_request", forged.topic)
end
```
This demonstrates byte identity (`original.hmac == forged.hmac`) while `shop`/`topic` diverge and are both accepted by `HmacValidator.validate`, confirming the unauthenticated tenant relabeling.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
