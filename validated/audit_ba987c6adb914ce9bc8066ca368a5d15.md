### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. The `shop` field is therefore an unauthenticated value that is trusted and forwarded to the app's webhook handler after HMAC validation "passes."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop` is read straight from the `shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC against the request and, if it passes, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`: [4](#0-3) 

Because `to_signable_string` never incorporates `shop`, the binding `authenticated_shop == shop_used_by_handler` does not hold: the HMAC only authenticates the *body*, not the *(body, shop)* pair. Any request carrying a `raw_body`/`hmac` pair that was genuinely signed by Shopify for one shop, but with the `X-Shopify-Shop-Domain` header rewritten to a different shop, will still pass `HmacValidator.validate` and will be dispatched to the app's handler labeled as coming from the attacker-chosen shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is expected to enforce for webhook processing: `process` is meant to guarantee "this body genuinely came from Shopify for shop X," but it only guarantees "this body genuinely came from Shopify for *some* shop," while `shop` is taken on faith. An attacker who can capture or replay one legitimate webhook delivery (e.g., from their own store, or via a webhook that was ever exposed/logged) can relabel it as belonging to a different tenant. Any downstream logic in `handler.handle` that uses `WebhookMetadata#shop` to select the store record, resolve stored offline access tokens, or apply per-tenant business logic will act on the wrong tenant's context, producing cross-tenant data confusion.

### Likelihood Explanation
Exploitation requires possession of a single valid `(raw_body, hmac)` pair, which any merchant/app-owner of any single shop naturally has (from their own webhook deliveries). No `client_secret` or access token is needed to construct the forged header — only network access to the app's webhook endpoint and a previously observed valid delivery. Endpoint host/routing controls are not part of this gem's guarantees, so the header is fully attacker-controlled at the HTTP layer.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signable string bound to the HMAC check, or otherwise cryptographically bind the shop domain header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and/or enforce that `request.shop` must be cross-checked against an independently authenticated source (e.g., the shop associated with the session/access token used to register the webhook) before being used for tenant-scoped actions.

### Proof of Concept
1. Attacker owns/operates `shop-a.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for secret `S`).
2. Attacker replays the request to the app's webhook endpoint, keeping `body = B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `shop-b.myshopify.com` while `to_signable_string` still returns `B`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` with `Context.api_secret_key` and it matches `H` → validation succeeds.
5. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)`, i.e., data genuinely originating for shop-a is now processed under shop-b's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
