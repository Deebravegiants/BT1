### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing via HMAC-valid webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which tenant the webhook belongs to when constructing `WebhookMetadata` and dispatching it to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop` accessor, however, is read straight from the `shop-domain` header, which is never part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC (over body only) and then immediately trusts `request.shop` to build the `WebhookMetadata` that is handed to the application's handler: [4](#0-3) 

`WebhookMetadata#shop` is a plain `const :shop, String` field with no further validation, and it is this value the app is expected to trust to know which shop/tenant the payload belongs to: [5](#0-4) 

This is directly analogous to the reported bug class: a field ("shop") is acted on to establish tenant identity but is not covered by the integrity check (HMAC), exactly like the report's `approve()` calls acting on state that isn't properly reset/bound before use. Here, the identity binding "authenticated tenant == shop field consumed by the handler" is broken because the HMAC only binds the body, not the shop header.

**Exploit path**: An attacker who operates or controls any shop with your app installed receives legitimate webhooks for their own shop, including a valid `hmac-sha256`/`shop-domain` header pair (computed by Shopify over the body only). The attacker can replay that exact body + HMAC to your app's webhook endpoint while substituting the `shop-domain` (and/or `x-shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` will still succeed, because the check never inspects the header, only the raw body against the secret. `Registry.process` will then dispatch `WebhookMetadata` labeled with the victim's shop domain to the handler, which will act on/store data as if it came from the victim tenant.

### Impact Explanation
This breaks the equality "HMAC-authenticated request originates from shop X" == "`request.shop` reported to the handler is X". Any handler logic that uses `data.shop` to select which tenant's records to update, to look up a per-shop session/access token, or to authorize an action, can be tricked into operating on/writing into another merchant's tenant context, using only content the attacker legitimately received for their own store. This is a cross-tenant data confusion vector rooted in the gem's webhook verification design (only the body is bound by HMAC), which qualifies under the cross-tenant access impact category.

### Likelihood Explanation
Requires only that the attacker control one shop with the app installed (unprivileged relative to other tenants) and be able to send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `client_secret`, or privileged credentials of the app are needed — only knowledge of the webhook header names, which are documented by Shopify. Likelihood is high for any app whose webhook handler trusts `WebhookMetadata#shop` for tenant selection, which is the documented, expected usage pattern of this gem.

### Recommendation
Either (a) do not trust the `shop`/`shop-domain` header for tenant identification without further verification (e.g., re-check the shop belongs to a domain that installed the app and correlate it against a session store keyed by shop, not solely by header value), or (b) document explicitly that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by callers, or (c) extend `to_signable_string`/verification to require an out-of-band correlation (e.g., matching the topic/webhook_id against Shopify's registered webhook subscription for the claimed shop before dispatch).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers/receives a webhook (e.g. `orders/create`), capturing the raw body and its `x-shopify-hmac-sha256` header.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only compares the HMAC against `@raw_body`: [6](#0-5) 
4. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is `"victim-shop.myshopify.com"`, despite the payload never having been authenticated as coming from that shop: [7](#0-6)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
