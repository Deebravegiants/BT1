### Title
Webhook `shop` identity field is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, then trusts an unauthenticated header to determine which shop (tenant) the webhook belongs to. The `shop` value handed to the app's handler is never bound to the HMAC that "proves" the request is legitimate, breaking the identity binding: `hmac_valid(body) == true` is treated as `shop_header == authenticated_shop`, which does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request` computes the value verified by HMAC from the raw body only: [1](#0-0) 

The `shop` accessor, in contrast, is read directly from an attacker-influenced HTTP header, with no participation in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's registered handler: [3](#0-2) 

`HmacValidator.validate` only checks that the (attacker-supplied) body/hmac pair matches the app's single, shop-independent `client_secret` (`Context.api_secret_key`), which is the same key for every shop that installed the app: [4](#0-3) 

Because the `client_secret`/HMAC key is shared across all shops that installed an app, and the HMAC covers only the body (not the `X-Shopify-Shop-Domain` header), a request with a *previously observed, validly-signed* `(body, hmac)` pair can be replayed with an arbitrary `shop` header and will still pass `HmacValidator.validate`. The library's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request — including the shop attribution — is authenticated, which is not the case: [5](#0-4) 

### Impact Explanation
This breaks the tenant identity binding `authenticated_shop == shop_used_for_data_attribution`. An attacker who has legitimately installed the app for their own shop (or otherwise obtains one valid `(body, hmac)` pair for the app, e.g. from their own store's webhook traffic, which they fully control and can observe) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop`/`shop-domain` header for a victim shop that also installed the same app. `Registry.process` will validate the HMAC (it is valid — it was legitimately produced with the shared `client_secret`) and hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop. Any host application that uses `data.shop` from `WebhookHandler#handle` to select which tenant's records to create/update/delete (the exact usage shown in the gem's own documentation, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) will process attacker-controlled data under the wrong tenant's identity — a cross-tenant data-integrity/isolation break.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be a legitimate installer of the vulnerable app on at least one shop (an "unprivileged internet user" relative to any other tenant), and (2) a second shop it wants to target also uses the app. No access to `api_secret_key`, tokens, or privileged credentials is needed — the attacker uses their own legitimately-received, correctly-signed webhook traffic and merely modifies an unauthenticated header before replaying it.

### Recommendation
Include the shop domain (and other identity-relevant headers such as `webhook_id`/`api_version` if used for deduplication logic) in the signable payload that `HmacValidator` verifies, or otherwise cryptographically bind the shop identity to the request (e.g., verify that the `shop` header corresponds to a shop with an active registration/session known to the app before dispatching to the handler). At minimum, update the documentation/`WebhookMetadata` contract to make clear that `shop` is not covered by the HMAC and must not be trusted for tenant attribution without additional verification by the host application.

### Proof of Concept
1. Attacker installs App under `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `App`'s single `client_secret`), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the same `B`/`H` pair to the app's webhook endpoint, replacing the shop header with `victim.myshopify.com` (a shop that also installed `App`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H})` is constructed.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` using the app's single `Context.api_secret_key` and matches `H` — validation succeeds. [6](#0-5) 
5. The handler is invoked with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-supplied data as if it belonged to `victim.myshopify.com`. [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
