### Title
Webhook shop/topic attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that `ShopifyAPI::Webhooks::Registry.process` uses to attribute and dispatch the webhook are read from unauthenticated HTTP headers. An attacker who can obtain any single validly-signed webhook payload (e.g. by installing the app on their own store) can replay it against the app's public webhook endpoint while swapping the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to make the app process the event as if it belonged to a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from request headers with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then constructs `WebhookMetadata` (including `shop` and `topic`) directly from these unauthenticated header fields and dispatches it to the registered handler: [3](#0-2) 

The identity binding that should hold is: `shop-header == shop-covered-by-hmac`. In this implementation, the HMAC only proves "this body was signed with the app's `api_secret_key`" — it says nothing about which shop or topic the signer intended. Any `(raw_body, hmac)` pair that is valid for one shop/topic is equally valid (per `HmacValidator.validate`, which only recomputes over `to_signable_string`, i.e. the body) when replayed with different `shop-domain`/`topic` headers: [4](#0-3) 

### Impact Explanation
An unprivileged internet user who is able to install the target app on their own (attacker-controlled) development store will legitimately receive real, correctly-signed webhook deliveries from Shopify for their own shop. Because `shop`/`topic` are not part of the signed content, the attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to any other merchant's shop domain (and/or the `x-shopify-topic` header changed to any registered topic). The app's handler will receive `WebhookMetadata` claiming that event originated from the victim shop and act on it accordingly — this is a cross-tenant identity confusion that lets an attacker who controls no more than their own shop trigger arbitrary registered webhook handlers (e.g. `app/uninstalled`, `shop/redact`, order/customer state-changing handlers) against a shop the attacker does not own, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be able to install the target app once on any shop they control (a normal, unprivileged action for any Shopify developer/merchant), (2) capture one signed webhook delivery for their own shop, and (3) send an HTTP POST to the app's known webhook endpoint with modified, unsigned headers. No access to `api_secret_key`, tokens, or the victim's credentials is required, making this readily reachable by any external actor.

### Recommendation
Include the security-relevant identity fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed content, or otherwise independently authenticate the `shop-domain` header (e.g. compare it against an active session/shop the app has already granted webhook registration for) before dispatching to handlers. At minimum, document that consuming apps must not trust `request.shop`/`request.topic` unless they can independently corroborate them, and add a `assert`-style consistency check that rejects requests whose headers were not derived from the signed payload.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook from Shopify:
raw_body   = '{"id":123,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
) # only Shopify can compute this, but the attacker legitimately receives it

captured_headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "attacker.myshopify.com",
}

# 2. Attacker replays the SAME (raw_body, hmac) pair to the app's public
#    webhook endpoint, but swaps the shop-domain header to a victim shop.
forged_headers = captured_headers.merge(
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
)

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation still passes because it only checks raw_body vs secret:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 3. Registry.process dispatches to the handler believing the event
#    is for "victim-shop.myshopify.com":
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", ...))
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
