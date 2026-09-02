### Title
Webhook `shop` identity field is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only, but the `shop` (and `topic`/`webhook_id`) values used by `Registry.process` to attribute the webhook to a tenant are taken from unauthenticated HTTP headers that are never included in the signed bytes. This is the same class of bug as the reported analog: a field that is *acted on* (here, the tenant-identifying `shop`) is not covered by the integrity check (`HMAC`) that is supposed to bind the whole message.

### Finding Description
`Utils::VerifiableQuery#to_signable_string` is what `HmacValidator.validate` uses to recompute the expected signature and compare it (via `OpenSSL.secure_compare`) against the caller-supplied `hmac`. [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers supplied by the caller, and are not part of the signed string at all: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then dispatches to the app's handler using the *header-derived* `shop`, `topic`, and `webhook_id`, with no cross-check that these headers are consistent with anything cryptographically bound to the body: [4](#0-3) [5](#0-4) 

**Binding that should hold:** `shop_header == shop_bound_by_hmac(body)`.
**Binding that actually holds:** `hmac_valid(body) ∧ shop_header == shop_header` — i.e. `shop` is never checked against anything the HMAC covers. The equality the code relies on is trivially true and provides no authentication of the `shop` value.

**Attack sequence:**
1. Attacker owns/operates their own Shopify store (`attacker-shop.myshopify.com`) with the target app installed, so Shopify legitimately delivers the attacker a real webhook: `raw_body = B`, header `shopify-shop-domain: attacker-shop.myshopify.com`, header `shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker replays this exact `raw_body` and `hmac` header to the app's webhook endpoint, but substitutes the `shopify-shop-domain` header (and optionally `shopify-topic`/`shopify-webhook-id`) with a victim shop's domain.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` — unchanged, since only `raw_body` is signed — and it still matches the supplied `hmac`, so validation passes.
4. `Registry.process` dispatches the webhook to the app's handler with `shop: "victim-shop.myshopify.com"` even though the body content actually originated from, and was only proven authentic for, the attacker's own shop.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce for inbound webhooks: an app's webhook handler is meant to trust that `HMAC` validation proves both the payload integrity *and* the originating shop. Here, only the payload bytes are authenticated — the `shop` attribution is attacker-controlled. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up a stored access token/session for that shop to act on the payload, triggering GDPR mandatory-topic handling such as `shop/redact` or `customers/redact` for the wrong merchant, or updating per-shop state), this enables cross-tenant data confusion/injection using data attributed to a shop that never sent it. This aligns with the Critical "cross-tenant access" impact category, since the gem itself hands the application webhook data falsely attributed to another authenticated tenant.

### Likelihood Explanation
Any unprivileged user capable of installing the app on their own store (a normal, low-privilege action for any Shopify merchant) can generate a valid `(body, hmac)` pair without needing the app's `client_secret` or any other privileged credential — they only need to capture headers from a webhook delivered to their own endpoint/store, then re-POST it to the app's webhook route with a forged `shop-domain` header. This requires no host-application misconfiguration; it results directly from `Request#to_signable_string` only committing to the raw body while `Registry.process`/`WebhookHandler` treat the header-derived `shop` as trusted.

### Recommendation
Include the shop-identifying and routing fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or otherwise cryptographically bind them to the request (e.g., verify the header-derived `shop` against a value embedded in, or independently signed with, the payload) before dispatching to `WebhookHandler#handle`. At minimum, document and enforce that the transport layer (e.g., mutual TLS or an allow-list of Shopify's webhook source IPs) is the only thing preventing an unauthenticated header spoof, since the HMAC currently provides no such guarantee for `shop`.

### Proof of Concept
```ruby
# Attacker legitimately receives this webhook for THEIR OWN shop:
raw_body = '{"id":1,"event":"order_created"}'
real_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
)

# Attacker replays it to the app's webhook endpoint, swapping only the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac,           # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation succeeds (it only checks raw_body),
#    handler.handle is invoked with shop: "victim-shop.myshopify.com"
``` [4](#0-3)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
