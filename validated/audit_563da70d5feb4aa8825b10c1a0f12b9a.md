Confirmed: the `WebhookMetadata.shop` field passed to the host app's handler is sourced entirely from an unauthenticated HTTP header, while the HMAC only covers the raw body.

### Title
Webhook shop-domain/topic identity spoofing via HMAC that only covers the body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, but `to_signable_string` (used by the HMAC check) only returns the raw request body. `Registry.process` validates the HMAC against the body alone and then trusts the header-derived `shop`/`topic` values to build `WebhookMetadata` handed to the host app's handler. Because the identity fields are not covered by the signature, any holder of a valid `(raw_body, hmac)` pair for the shared app secret can relabel that payload as coming from any shop or topic.

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, raw_body || shop || topic)` for the `shop`/`topic` values that are subsequently trusted. Instead the code computes and checks: [1](#0-0) 
which signs only `@raw_body`. The `shop` and `topic` accessors read straight from headers with no cryptographic binding to that signature: [2](#0-1) 

`Registry.process` performs the HMAC check and then immediately trusts `request.topic` and `request.shop` to construct the metadata passed to the app-registered handler: [3](#0-2) 

The HMAC validator itself only ever compares against `verifiable_query.to_signable_string`, i.e. the body: [4](#0-3) 

Since a single app uses one `api_secret_key` shared across every shop that installs it, any unprivileged merchant who installs the app receives genuinely-signed webhooks for their own store (Shopify computes the HMAC over the body using that shared secret). That merchant can capture a `(raw_body, hmac)` pair from their own legitimate webhook delivery and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to name a different, victim shop. The HMAC still validates because it never covered those headers, so `Registry.process` will dispatch the handler with `WebhookMetadata#shop` claiming to be the victim's shop while carrying attacker-controlled body content.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically-verified payload and the shop it is attributed to, letting an unprivileged app installer inject data/events that the host application will process as originating from an arbitrary other tenant (cross-tenant access/injection) without ever needing the victim's credentials or the app's `client_secret` directly — only a legitimately-signed webhook of their own is required as the raw material.

### Likelihood Explanation
Any merchant who installs the app can trivially trigger a webhook to themselves (e.g. by performing the action that the subscribed topic corresponds to), capture the exact bytes and HMAC, and replay them with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. No special privileges, secrets, or timing constraints are required beyond normal app installation.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook_id`/`api_version`) in the signed material that `HmacValidator` checks, or independently verify that the `shop-domain` header matches a shop known to be associated with the currently registered/active session before dispatching to `WebhookHandler#handle`. At minimum, `Request#to_signable_string` should not be limited to the raw body when the shop/topic identity extracted from headers is trusted downstream.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a webhook subscribed by the app (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(secret, B)` — attacker captures this request.
3. Attacker replays the identical body `B` and header `x-shopify-hmac-sha256: H` to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` and/or a different `x-shopify-topic`.
4. `Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `B`, matching `H`.
5. `Registry.process` builds `WebhookMetadata.new(topic: "attacker-chosen", shop: "victim.myshopify.com", body: parsed(B), ...)` and invokes the registered handler, which processes attacker-controlled data as if it came from the victim shop.

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
