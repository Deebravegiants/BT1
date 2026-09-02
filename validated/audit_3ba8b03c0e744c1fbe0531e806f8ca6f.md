## Finding

The HMAC verification for inbound webhooks only covers the raw request body — it does not bind the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that the gem uses to dispatch the request and identify the tenant. [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, so for a webhook `Request` the *only* HMAC-protected content is the JSON body. [2](#0-1) 

Yet `ShopifyAPI::Webhooks::Registry.process` reads the shop identity and topic straight from the unauthenticated headers and feeds them, unchecked, into the handler as the trusted tenant/topic context: [3](#0-2) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

Both `request.shop` and `request.topic` come straight from the `shopify-shop-domain` / `x-shopify-shop-domain` and `shopify-topic` / `x-shopify-topic` headers, which are never part of the signed payload. [4](#0-3) 

### Title
Webhook handler dispatch trusts `shop`/`topic` headers that are excluded from the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `HmacValidator.validate` authenticates body bytes only. `ShopifyAPI::Webhooks::Registry.process` nevertheless uses the caller-supplied `shop-domain` and `topic` headers — which carry zero cryptographic binding — to select the handler and to populate `WebhookMetadata#shop`/`#topic`, the values app code relies on to scope data per tenant.

### Finding Description
The HMAC binding equality that should hold is:
`hmac_verified_bytes == (raw_body, shop, topic, webhook_id, api_version)`

In this codebase the equality actually enforced is:
`hmac_verified_bytes == raw_body` only, while `shop`/`topic` are read straight from client-supplied headers with no signature coverage (`lib/shopify_api/webhooks/request.rb:35-38`, `:20-23`, `:15-18`). `Registry.process` then trusts these unauthenticated header values for both handler routing (`@registry[request.topic]`) and for the `shop` field surfaced to the app's business logic (`lib/shopify_api/webhooks/registry.rb:189-199`).

Since a single shared `api_secret_key` signs webhook bodies for every shop and every topic subscribed by the app, once an attacker obtains one valid `(raw_body, hmac)` pair — e.g. from a webhook delivered to a merchant-controlled endpoint during development/testing, or from any tunneling/proxy the merchant operates to inspect their own store's webhook traffic — that exact body+HMAC pair remains valid when replayed to the app's production webhook endpoint with a different `shop-domain` or `topic` header. The gem performs no check that the signed content is consistent with the routing headers.

### Impact Explanation
This breaks the tenant/topic identity binding that multi-tenant Shopify apps rely on: an attacker who legitimately owns one shop (or otherwise observes one valid webhook delivery) can forge webhook events that the receiving app will process as belonging to a *different* shop or a *different* topic than the one Shopify actually signed. Because `WebhookMetadata#shop` is the field apps use to scope database writes/deletes (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`), this enables cross-tenant data corruption/disclosure without ever needing the app's `client_secret` or an access token — meeting the "cross-tenant access" Critical-impact bar.

### Likelihood Explanation
Exploitation requires only one legitimately-observed `(body, hmac)` pair (trivially available to any shop owner who proxies/logs their own store's webhook deliveries, since HMAC never changes based on shop or topic) plus the ability to POST to the app's public webhook endpoint — no leaked secret, no privileged account, and no host-side misconfiguration required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable content verified against the HMAC (or independently cross-check the body's own shop-scoped identifiers against the headers before dispatch), so that the values used for routing and tenant identification are cryptographically bound to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and runs the app's webhook endpoint behind a debugging proxy they control, capturing a legitimate `orders/create` delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)` and does not depend on shop/topic).
2. Attacker POSTs body `B` with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: victim.myshopify.com`, `x-shopify-topic: orders/create` (or any registered topic) directly to the app's webhook endpoint.
3. `HmacValidator.validate` succeeds because it only checks `B` against `H`.
4. `Registry.process` dispatches the handler with `WebhookMetadata(shop: "victim.myshopify.com", topic: ..., body: parsed(B))`, causing the app to act as though `victim.myshopify.com` sent this event.

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
