### Title
Webhook shop/topic attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating the HMAC over the raw request body only, then unconditionally trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers — none of which are covered by that signature — when constructing the `WebhookMetadata` passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All the other request attributes — `topic`, `shop`, `api_version`, `webhook_id` — are parsed straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body bytes were signed with the app's secret) and then immediately builds `WebhookMetadata` from the *unverified* header fields, handing it to the registered handler as trusted tenant/topic context: [3](#0-2) 

This is the same bug class as the referenced report: a value the code acts on (`shop`, `topic`, `webhook_id`) is not covered by the authentication primitive (`HmacValidator.validate`) that is supposed to establish trust for the request as a whole. `HmacValidator.validate_signature` binds trust only to `verifiable_query.to_signable_string`, i.e. the raw body: [4](#0-3) 

Because the signature never binds to `shop-domain`/`topic`/`webhook-id`, any party who can produce or capture one valid `(body, hmac)` pair signed with the app's secret (e.g. a webhook the attacker legitimately receives for their own store) can replay that exact body with the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers swapped to arbitrary values. `Registry.process` will still consider the request "valid" (HMAC check passes because the body is unchanged) and will dispatch to the handler with attacker-chosen `shop`/`topic`/`webhook_id` in `WebhookMetadata` — exactly the officially documented mechanism apps are told to use to attribute the webhook to a tenant.

Binding broken (equality that should hold but doesn't):
`shop/topic/webhook_id delivered to handler == shop/topic/webhook_id actually authenticated by HMAC` — in this gem, the left side is attacker-controlled header input while the right side is always empty (the signature only covers the body).

### Impact Explanation
An app that follows the gem's documented pattern (using `WebhookMetadata#shop` from `Registry.process` to route data/actions to the correct merchant record) can be tricked into applying webhook side effects (e.g. redact/data-request handling, entitlement changes, inventory/order updates) to the wrong tenant, using a signature that was never issued for that tenant. This is a cross-tenant integrity break rooted entirely in this gem's trust model (`Registry.process` + `Request`), independent of any host-app misuse.

### Likelihood Explanation
The prerequisite is capturing any one legitimate `(body, hmac)` pair — trivial for any actual/former merchant of the app, or anyone who can observe one webhook delivery (e.g. from their own store, or via a proxy/log). No `client_secret` or access token is needed; only a header rewrite on replay.

### Recommendation
Include the tenant/topic-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material used by `Request#to_signable_string`/`HmacValidator`, or otherwise cryptographically bind them (e.g., derive `shop` only from a value that Shopify signs, or require the app to independently confirm the `shop` header matches an existing, previously-established session/store before trusting `WebhookMetadata`). At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are NOT authenticated by `Registry.process` and must not be used for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker operates (or once operated) store A and receives a genuine webhook from Shopify: body `B`, headers `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: store-a.myshopify.com`, `X-Shopify-Topic: orders/create`.
2. Attacker replays the exact same request to the app's webhook endpoint but changes `X-Shopify-Shop-Domain` to `store-b.myshopify.com` (a victim tenant) and leaves body `B` and `H` untouched.
3. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)` over `request.to_signable_string` (= body `B` only) — validation succeeds because the body/HMAC pair is unchanged.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `store-b.myshopify.com`, and invokes the app's handler as if Shopify had genuinely sent this webhook for store B. [5](#0-4)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
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
