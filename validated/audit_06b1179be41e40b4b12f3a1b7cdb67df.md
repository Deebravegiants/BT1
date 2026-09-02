## Title
Webhook HMAC only signs the raw body while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated headers, allowing a shop-domain spoof with a replayed valid signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates nothing but the JSON body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` extracts and hands to the app's webhook handler as the tenant/event identity are read straight from HTTP headers that are outside the HMAC computation.

### Finding Description
`Registry.process` performs exactly one authentication check before dispatching to the handler: [1](#0-0) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`: [3](#0-2) 

For `Webhooks::Request`, `to_signable_string` is defined as just the raw body — none of the header-derived fields participate in the signature: [4](#0-3) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that are never mixed into the HMAC input: [5](#0-4) 

This breaks the identity binding `shop_authenticated == shop_used_for_dispatch`. The only thing the HMAC actually proves is "this body byte-string was produced with knowledge of the app's `client_secret`" — it says nothing about which shop, topic, or webhook id the body is associated with.

### Impact Explanation
Because the app's `client_secret` (and therefore the HMAC) is identical for every shop that installs the app, any merchant who legitimately installs the app can capture a `(raw_body, hmac)` pair from one of their own real webhook deliveries. That pair carries a signature that will pass `HmacValidator.validate` for a replayed request to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header rewritten to a *different* victim shop. `Registry.process` will then invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop while `body`/`topic` are attacker-controlled but validly signed. Any host application that uses `data.shop` from the handler callback to scope database writes, cache invalidation, uninstall/GDPR flows, or other per-tenant side effects (which is the documented usage pattern for this API) can be tricked into performing that side effect against another merchant's tenant — a cross-tenant data integrity/write vector triggered purely from the perspective of a co-tenant, unprivileged relative to the victim shop.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate installer of the same app on their own store (a normal unprivileged action for any public/embedded Shopify app) and the ability to send an HTTP POST to the app's public webhook endpoint with modified headers and the replayed body/hmac — no access token, `client_secret`, or privileged account is needed. The likelihood of this succeeding is entirely dependent on whether the consuming application trusts `WebhookMetadata#shop`/`#topic` for tenant scoping without any secondary check, which is the pattern this gem's own documentation encourages.

### Recommendation
Bind the header-derived identity fields into the signed material, e.g. have `Webhooks::Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` (canonicalized) alongside the raw body, or otherwise require the host application to independently verify `shop` against a known/installed-shop list before trusting `WebhookMetadata#shop`. At minimum, document prominently that `shop`/`topic`/`webhook_id` are NOT covered by the HMAC and must not be used for authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
2. Attacker replays the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if the handler keys off those).
3. `HmacValidator.validate` succeeds because `to_signable_string` only checks `raw_body`, which is unchanged.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to act as if the event came from `victim-shop`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
