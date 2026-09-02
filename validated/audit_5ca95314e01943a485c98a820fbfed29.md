## Finding [1](#0-0) [2](#0-1) 

### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, then trusts the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers to build the `WebhookMetadata` handed to the app's handler. Because those identity fields are never part of the signed content, any actor who can produce (or replay) a body/HMAC pair that is valid for the app's secret can attach an arbitrary `shop`/`topic`/`webhook_id` to that payload, causing the receiving app to process data under the wrong tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC only against `verifiable_query.to_signable_string`, i.e., only the body:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [4](#0-3) 

`Registry.process` gates only on this body-HMAC check, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id`, all of which come straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) that are **not** part of the signed bytes:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [2](#0-1) 

and the headers themselves:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def webhook_id
  T.cast(shopify_header("webhook-id"), String)
end
``` [5](#0-4) 

The binding that should hold is:
`bytes verified by HMAC == bytes the handler relies on for tenant identity (shop, topic, webhook_id)`

Here that equality fails: the bytes verified are just `@raw_body`, while the bytes the handler receives and trusts for routing/tenant-scoping (`shop`, `topic`, `webhook_id`) come from separate, unsigned header fields. Any party capable of obtaining one valid `(body, HMAC)` pair for the app's secret (e.g., a merchant who installs the app on their own store and captures their own legitimate webhook delivery) can resend that exact body/HMAC pair to the app's webhook endpoint with the `shopify-shop-domain` header swapped to a victim shop, and/or the `shopify-topic`/`shopify-webhook-id` headers changed. `Registry.process` will accept it as valid (the body HMAC still checks out) and hand the attacker-chosen `shop`/`topic` to the app's webhook handler as if Shopify had sent that data for that shop/topic.

### Impact Explanation
This breaks the tenant-identity binding a multi-tenant Shopify app relies on: the HMAC is meant to prove "this data came from Shopify for this specific shop/topic," but the shop and topic are never actually authenticated. An attacker who can obtain any valid signed webhook body (trivially, by being a legitimate but hostile merchant of the app) can cause the receiving application to attribute that body to a different shop or a different topic than what was actually signed, resulting in cross-tenant data confusion in downstream processing (e.g., data intended for shop A being recorded/acted upon under shop B's tenant record, or a body meant for one webhook topic being routed to a handler for another topic). This falls under cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only a body+HMAC pair valid for the target app's `api_secret_key` — which any real merchant/customer of a multi-tenant app can obtain simply by triggering a legitimate webhook on their own store (no leaked secret needed). Replaying that request with modified `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id` headers is trivial for anyone who can reach the app's public webhook endpoint.

### Recommendation
Bind the shop/topic/webhook_id identity to the signed content, e.g., include these header values in the signable string (or otherwise cryptographically bind them, since Shopify's own signature only covers the body) is not something this library controls on the wire format — but at minimum, the gem should document/require callers to independently corroborate `shop`/`topic` against a known, expected value (e.g., the shop tied to the currently active session/tenant) before trusting `WebhookMetadata`, and/or the library could expose a stricter validation mode that rejects headers that don't match the topic registered for the expected shop context.

### Proof of Concept
1. App merchant M installs the target app; Shopify sends a legitimate webhook to the app's endpoint with body `B`, header `shopify-hmac-sha256: HMAC(B)`, and `shopify-shop-domain: m-shop.myshopify.com`.
2. M (attacker) captures this request.
3. M resends the identical body `B` and HMAC header, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and/or changes `shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B)` against the body — this still passes.
5. The webhook handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes `B`'s contents as if they belonged to `victim-shop`, even though Shopify never sent that data for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
